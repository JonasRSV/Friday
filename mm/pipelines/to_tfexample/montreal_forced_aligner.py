import numpy as np
import textgrid
import argparse
import sox
import pathlib
import shared.tfexample_utils as tfexample_utils
import tensorflow as tf
from tqdm import tqdm
from typing import Mapping


class Alignments:
    def __init__(self):
        self.word_counts = {}


def alignments_pass(alignments: pathlib.Path) -> Alignments:
    """Peform a single pass on all alignments to calculate meta information."""

    meta = Alignments()

    for speaker in tqdm(list(alignments.glob("*")), desc="Alignment Pass"):

        # To ignore hidden files etc.
        if str(speaker.stem).isnumeric():
            for grid in speaker.glob("*.TextGrid"):
                tg = textgrid.TextGrid.fromFile(grid)
                for interval in tg[0]:
                    start_time = interval.minTime
                    end_time = interval.maxTime
                    text = interval.mark

                    if text:
                        if text not in meta.word_counts:
                            meta.word_counts[text] = 0

                        meta.word_counts[text] += 1

    return meta


class Writers:
    """Class containing the recordIO writers."""

    def __init__(self, base: pathlib.Path, words: [str]):
        self.base = base
        self.words = words

        self.writers = {}
        for word in words:
            self.writers[word] = tf.io.TFRecordWriter(str(self.__path(word)))

    def __path(self, word: str):
        return self.base / f"tfexamples.{word}.mfa"

    def write(self, word: str, sample_rate: int, audio: [int]):
        example = tfexample_utils.create_example(
            audio=audio,
            text=word,
            sample_rate=sample_rate
        )

        self.writers[word].write(example.SerializeToString())

    def __del__(self):
        for writer in self.writers.values():
            writer.close()


def get_words_to_convert(meta: Alignments,
                         min_occurrences: int,
                         min_word_length: int) -> [str]:
    """The words to include in the common dataset"""
    return [word for word, occurrences in meta.word_counts.items()
            if occurrences >= min_occurrences
            and word != "<unk>"
            and len(word) > min_word_length
            ]


def get_word_probabilities(meta: Alignments, words: [str], target_occurrences: float) -> [float]:
    """A probability to include an occurrence of a word for each word.

    This probability is used to try to make sure we get about 'target_occurrences' number of occurrences for each word,
    where it is possible. We do it using probabilities to get a even spread to avoid just picking all occurrences from
    one speaker.
    """
    return [min(target_occurrences / meta.word_counts[word], 1) for word in words]


def create_datapoints(transformer: sox.Transformer,
                      writers: Writers,
                      word_probability: Mapping[str, float],
                      grid: pathlib.Path,
                      audio: pathlib.Path):
    """Creates datapoints from a TextGrid."""
    audio_file = audio / grid.parts[-2] / f"{grid.stem}.wav"

    if audio_file.is_file():
        resampled_audio = transformer.build_array(
            input_filepath=str(audio_file)
        )

        tg = textgrid.TextGrid.fromFile(grid)
        for interval in tg[0]:
            start_time = interval.minTime
            end_time = interval.maxTime
            text = interval.mark

            if text in word_probability and word_probability[text] > np.random.rand():
                start_sample = int(max((start_time - 0.1) * transformer.output_format["rate"], 0))
                end_sample = int(min((end_time + 0.1) * transformer.output_format["rate"], resampled_audio.size))

                utterance = resampled_audio[start_sample:end_sample]

                writers.write(word=text,
                              sample_rate=transformer.output_format["rate"],
                              audio=utterance)

    else:
        print(f"File not found: {audio_file}")


def sample_pass(transformer: sox.Transformer,
                writers: Writers,
                words: [str],
                probabilities: [float],
                audio: pathlib.Path,
                alignments: pathlib.Path):
    """Perform a pass to sample data for the dataset.

    During this pass the actual dataset is also created.
    """
    word_probability = {word: probability for word, probability in zip(words, probabilities)}

    for speaker in tqdm(list(alignments.glob("*")), desc="Alignment Pass"):

        # To ignore hidden files etc.
        if str(speaker.stem).isnumeric():
            for grid in speaker.glob("*.TextGrid"):
                create_datapoints(transformer=transformer,
                                  writers=writers,
                                  word_probability=word_probability,
                                  grid=grid,
                                  audio=audio)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--alignments", type=pathlib.Path, required=True, help="Directory of forced alignments")
    parser.add_argument("--audio", type=pathlib.Path, required=True, help="Directory of audio files")
    parser.add_argument("--sink", type=pathlib.Path, required=True, help="Output directory to write dataset")
    parser.add_argument("--min_occurrences", type=int, required=True,
                        help="Minimum number of times a word should occur")
    parser.add_argument("--min_word_length", type=int, required=True,
                        help="Minimum length of word")
    parser.add_argument("--target_occurrences", type=int, required=True,
                        help="Number of times we aim for a word to occur")
    parser.add_argument("--words_per_pass", type=int, default=100,
                        help="Number of word-files to create per pass")
    parser.add_argument("--sample_rate", type=int, default=8000,
                        help="Sample rate to convert data to.")

    args = parser.parse_args()

    meta = alignments_pass(args.alignments)
    words = get_words_to_convert(meta,
                                 args.min_occurrences,
                                 args.min_word_length)
    print(f"N words: {len(words)} ")
    probabilities = get_word_probabilities(meta, words, args.target_occurrences)

    iterators = [zip(words, probabilities)] * args.words_per_pass
    batches = zip(*iterators)

    transformer = sox.Transformer()
    transformer.set_output_format(rate=args.sample_rate, channels=1)
    for batch in tqdm(list(batches), desc="Sample Pass"):
        words, probabilities = zip(*batch)

        writers = Writers(args.sink, words)

        sample_pass(
            transformer=transformer,
            writers=writers,
            words=words,
            probabilities=probabilities,
            audio=args.audio,
            alignments=args.alignments
        )
