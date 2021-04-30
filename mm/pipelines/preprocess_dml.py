import sys
import os

# Some systems dont use the launching directory as root
sys.path.append(os.getcwd())

import tensorflow as tf
import argparse
import shared.tfexample_dma_utils as tfexample_dma_utils
import random
from pipelines.preprocessing.abstract_preprocess_fn import PreprocessFn
from pipelines.preprocessing.uppercase_text import TextUpperCase
from pipelines.preprocessing.filter_on_length import LengthFilter
from pipelines.preprocessing.random_bipadding import RandomBiPadding
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
    for example in source.glob("tfexamples*"):
        keyword = example.stem.split(".")[1]

        if keyword not in meta.word_files:
            meta.word_files[keyword] = []

        meta.word_files[keyword].append(example)

    meta.words = list(meta.word_files.keys())

    return meta


class Writers:

    def __init__(self, sink_prefix: str, expected_file_size: int, expected_total_size: int):
        self.expected_file_size = expected_file_size
        self.expected_total_size = expected_total_size

        self.writers = [
            tf.io.TFRecordWriter(f"{sink_prefix}-dml-{i}")
            for i in range(self.expected_total_size // self.expected_file_size)
        ]

        self.written_mb = 0

    def write(self,
              anchor: tf.train.Example,
              positive: tf.train.Example,
              negative: tf.train.Example):
        example = tfexample_dma_utils.create_example(anchor, positive, negative)
        example_bytes = example.SerializeToString()

        example_mbs = sys.getsizeof(example_bytes) / 1e6
        self.written_mb += example_mbs

        random.choice(self.writers).write(example_bytes)

        return example_mbs


def sample_files(utterances: Utterances) -> (Path, Path, Path):
    """Samples 3 files given all utterances.

    Returns: (anchor: Path, positive: Path, negative: Path)
    """
    anchor = random.choice(utterances.words)

    negative = random.choice(utterances.words)
    while negative == anchor:
        negative = random.choice(utterances.words)

    anchor_file = random.choice(utterances.word_files[anchor])
    positive_file = random.choice(utterances.word_files[anchor])
    negative_file = random.choice(utterances.word_files[negative])

    return anchor_file, positive_file, negative_file


def sample_triplets(samples: int, anchor_file: Path, positive_file: Path, negative_file: Path):
    anchor_examples = list(tf.data.TFRecordDataset(filenames=[str(anchor_file)]))
    positive_examples = list(tf.data.TFRecordDataset(filenames=[str(positive_file)]))
    negative_examples = list(tf.data.TFRecordDataset(filenames=[str(negative_file)]))

    anchor_examples = [tf.train.Example.FromString(example.numpy())
                       for example in random.choices(anchor_examples, k=samples)]

    positive_examples = [tf.train.Example.FromString(example.numpy())
                         for example in random.choices(positive_examples, k=samples)]

    negative_examples = [tf.train.Example.FromString(example.numpy())
                         for example in random.choices(negative_examples, k=samples)]

    return zip(anchor_examples, positive_examples, negative_examples)


def apply_map_fn(example: tf.train.Example,
                 map_fns: List[PreprocessFn]):
    for map_fn in map_fns:
        example = map_fn.do(example)[0]

    return example


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
    parser.add_argument("--expected_file_size", type=int, help="File size in MB",
                        default=100)
    parser.add_argument("--expected_total_size", type=int, help="File size in MB",
                        default=1 * 1000)
    parser.add_argument("--samples_per_instance", type=int, help="Number of samples to create per 'file' triple",
                        default=10)

    args = parser.parse_args()

    map_fns = [
        LengthFilter(max_length=args.clip_length, min_length=0.0),
        TextUpperCase(),
        RandomBiPadding(length=args.clip_length),
        AudioAugmentations()
    ]

    anchor_map_fns = [
        LengthFilter(max_length=args.clip_length, min_length=0.0),
        TextUpperCase(),
        RandomBiPadding(length=args.clip_length),
    ]

    utterances = meta_pass(args.source)
    writers = Writers(sink_prefix=args.sink_prefix,
                      expected_file_size=args.expected_file_size,
                      expected_total_size=args.expected_total_size)

    with tqdm(total=writers.expected_total_size) as progress_bar:
        while writers.written_mb <= writers.expected_total_size:
            anchor_file, positive_file, negative_file = sample_files(utterances)

            for anchor, positive, negative in sample_triplets(args.samples_per_instance,
                                                              anchor_file=anchor_file,
                                                              positive_file=positive_file,
                                                              negative_file=negative_file):

                # Lazy way of avoiding to check for mismatches between doFn and the mapFn
                try:
                    anchor = apply_map_fn(anchor, anchor_map_fns)
                    positive = apply_map_fn(positive, map_fns)
                    negative = apply_map_fn(negative, map_fns)

                    written_mbs = writers.write(anchor=anchor,
                                                positive=positive,
                                                negative=negative)

                    progress_bar.update(n=written_mbs)
                except Exception as e:
                    print(f"triplet construction failed, reason: {e}")

