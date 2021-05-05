# TODO: https://github.com/carlthome/python-audio-effects for augmentations
import sys
import os

# Some systems dont use the launching directory as root
sys.path.append(os.getcwd())

import numpy as np
import tensorflow as tf
import argparse
import shared.tfexample_dma_utils as tfexample_dma_utils
import random
import sox
from pipelines.preprocessing.filter_on_length import acceptable_length
from pipelines.preprocessing.random_bipadding import bipadding
from pipelines.preprocessing.audio_augmentations import AudioAugmentations
from tqdm import tqdm
from typing import Dict, List
from pathlib import Path

tf.compat.v1.enable_eager_execution()


class Utterances:
    """Meta information on all utterances"""

    def __init__(self):
        self.word_files: Dict[str, List[Path]] = {}
        self.words = []


def meta_pass(source: Path) -> Utterances:
    meta = Utterances()
    for word in source.glob("*"):
        if word.stem.startswith("."):
            print("ignoring hidden file", word)
            continue

        keyword = word.stem
        ##print("keywords", keyword)

        if keyword not in meta.word_files:
            meta.word_files[keyword] = []

        meta.word_files[keyword] = list(word.glob("*"))

    meta.words = list(meta.word_files.keys())

    return meta


class Writers:

    def __init__(self, sink_prefix: str, expected_file_size: int, expected_total_size: int):
        self.expected_file_size = expected_file_size
        self.expected_total_size = expected_total_size

        self.writers = [
            tf.io.TFRecordWriter(f"{sink_prefix}-{i}")
            for i in range(self.expected_total_size // self.expected_file_size)
        ]

        self.written_mb = 0

    def write(self,
              sample_rate: int,
              anchor_audio: np.ndarray,
              anchor_text: str,
              positive_audio: np.ndarray,
              positive_text: str,
              negative_audio: np.ndarray,
              negative_text: str):

        example = tfexample_dma_utils.create_example(sample_rate,
                                                     anchor_audio,
                                                     anchor_text,
                                                     positive_audio,
                                                     positive_text,
                                                     negative_audio,
                                                     negative_text)
        example_bytes = example.SerializeToString()

        example_mbs = sys.getsizeof(example_bytes) / 1e6
        self.written_mb += example_mbs

        random.choice(self.writers).write(example_bytes)

        return example_mbs


def sample_triplet(transformer: sox.Transformer, utterances: Utterances) -> ((np.ndarray, str), (np.ndarray, str), (np.ndarray, str)):
    anchor = random.choice(utterances.words)

    negative = random.choice(utterances.words)
    while negative == anchor:
        negative = random.choice(utterances.words)



    anchor_file = random.choice(utterances.word_files[anchor])

    positive_file = random.choice(utterances.word_files[anchor])
    while positive_file == anchor_file:
        positive_file = random.choice(utterances.word_files[anchor])

    negative_file = random.choice(utterances.word_files[negative])

   # print("anchor file", anchor_file)
   # print("positive file", positive_file)
   # print("negative file", negative_file)

    anchor_word = anchor_file.parent.stem
    anchor_audio = transformer.build_array(
        input_filepath=str(anchor_file)
    )

    positive_word = positive_file.parent.stem
    positive_audio = transformer.build_array(
        input_filepath=str(positive_file)
    )

    negative_word = negative_file.parent.stem
    negative_audio = transformer.build_array(
        input_filepath=str(negative_file)
    )

    #print("anchor-word", anchor_word)
    #print("positive-word", positive_word)
    #print("negative-word", negative_word)

    return (anchor_audio, anchor_word), (positive_audio, positive_word), (negative_audio, negative_word)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--source",
                        type=Path,
                        help="Prefix of input sharded file",
                        required=True)
    parser.add_argument("--sink_prefix",
                        type=str,
                        help="Prefix of output sharded file",
                        required=True)
    parser.add_argument('--clip_length', type=float,
                        help="All audio clips with length (seconds) longer than 'maximum_clip_length' will be chunked",
                        default=2)
    parser.add_argument('--sample_rate', type=int,
                        help="sample_rate of audio",
                        default=16000)
    parser.add_argument("--expected_file_size", type=int, help="File size in MB",
                        default=100)
    parser.add_argument("--expected_total_size", type=int, help="File size in MB",
                        default=1 * 1000)

    parser.add_argument("--augmentations", action="store_true", help="If should use augmentations on audio")

    args = parser.parse_args()

    if args.augmentations:
        augmentations = AudioAugmentations(sample_rate=args.sample_rate)

        pn_augmented = False

    def pn_map(audio: np.ndarray, text: str) -> (np.ndarray, str, bool):
        if not acceptable_length(args.clip_length, 0, audio, args.sample_rate):
            return (None, None, False)

        audio = bipadding(args.clip_length, audio, args.sample_rate)
        text = text.upper()

        if args.augmentations and np.random.rand() < 0.7:
            audio = augmentations.do(audio)
            pn_augmented = True
        else:
            pn_augmented = False


        return audio, text, True


    def anchor_map(audio: np.ndarray, text: str) -> (np.ndarray, str, bool):
        if not acceptable_length(args.clip_length, 0, audio, args.sample_rate):
            return (None, None, False)

        audio = bipadding(args.clip_length, audio, args.sample_rate)
        text = text.upper()

        if args.augmentations:
            if not pn_augmented:
                audio = augmentations.do(audio)
            elif np.random.rand() < 0.7:
                audio = augmentations.do(audio)

        return audio, text, True

    transformer = sox.Transformer()
    transformer.set_output_format(rate=args.sample_rate, channels=1)


    utterances = meta_pass(args.source)
    writers = Writers(sink_prefix=args.sink_prefix,
                      expected_file_size=args.expected_file_size,
                      expected_total_size=args.expected_total_size)

    with tqdm(total=writers.expected_total_size) as progress_bar:
        while writers.written_mb <= writers.expected_total_size:
            (anchor_audio, anchor_text), \
                (positive_audio, positive_text), \
                (negative_audio, negative_text) = sample_triplet(transformer, utterances)

            #try:
            (anchor_audio, anchor_text, anchor_ok) = anchor_map(anchor_audio, anchor_text)
            (positive_audio, positive_text, positive_ok) = pn_map(positive_audio, positive_text)
            (negative_audio, negative_text, negative_ok) = pn_map(negative_audio, negative_text)

            if anchor_ok == positive_ok == negative_ok == True:
                written_mbs = writers.write(args.sample_rate,
                                            anchor_audio,
                                            anchor_text,
                                            positive_audio,
                                            positive_text,
                                            negative_audio,
                                            negative_text)

                progress_bar.update(n=written_mbs)
            #except Exception as e:
            #    print(f"triplet construction failed, reason: {e}")

