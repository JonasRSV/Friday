import sys
import os

sys.path.append(os.getcwd())

import numpy as np
import textgrid
import argparse
import sox
import pathlib
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
                    text = interval.mark

                    if text:
                        if text not in meta.word_counts:
                            meta.word_counts[text] = 0

                        meta.word_counts[text] += 1

    return meta


class Writers:
    """Class containing the recordIO writers."""

    def __init__(self, 
                 transformer: sox.Transformer,
                 base: pathlib.Path,
                 words: [str]):
        self.transformer = transformer
        self.base = base
        self.words = words
        self.word_counts = {word: 0 for word in words}

    def __path(self, word: str):
        output_dir = self.base / word
        if not output_dir.is_dir():
            os.makedirs(output_dir)

        self.word_counts[word] += 1
        return self.base / word / f"mfa_align-{self.word_counts[word]}.wav"

    def write(self, word: str, sample_rate: int, audio: [int]):
        output_path = self.__path(word)

        self.transformer.build_file(
            input_array=np.array(audio, dtype=np.int16), sample_rate_in=sample_rate,
            output_filepath=str(output_path)
        )


def get_words_to_convert(meta: Alignments,
                         min_occurrences: int,
                         min_word_length: int) -> [str]:
    """The words to include in the common dataset"""
    return [word for word, occurrences in meta.word_counts.items()
            if occurrences >= min_occurrences
            and word != "<unk>"
            and len(word) >= min_word_length
            ]

def create_datapoints(transformer: sox.Transformer,
                      writers: Writers,
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

            if text in writers.word_counts:
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
                audio: pathlib.Path,
                alignments: pathlib.Path):
    """Perform a pass to sample data for the dataset.

    During this pass the actual dataset is also created.
    """
    for speaker in tqdm(list(alignments.glob("*")), desc="Dataset Pass"):

        # To ignore hidden files etc.
        if str(speaker.stem).isnumeric():
            for grid in speaker.glob("*.TextGrid"):
                create_datapoints(transformer=transformer,
                                  writers=writers,
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
    parser.add_argument("--sample_rate", type=int, default=8000,
                        help="Sample rate to convert data to.")

    args = parser.parse_args()

    meta = alignments_pass(args.alignments)
    words = get_words_to_convert(meta,
                                 args.min_occurrences,
                                 args.min_word_length)
    print(f"N words: {len(words)} ")

    transformer = sox.Transformer()
    transformer.set_output_format(rate=args.sample_rate, channels=1)

    writers = Writers(transformer, args.sink, words)

    sample_pass(
        transformer=transformer,
        writers=writers,
        words=words,
        audio=args.audio,
        alignments=args.alignments
    )
