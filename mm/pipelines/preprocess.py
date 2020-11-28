import sys
import os


# Some systems dont use the launching directory as root
sys.path.append(os.getcwd())

import shared.tfexample_utils as tfexample_utils
import pathlib
import json
from typing import List, Callable
import tensorflow as tf
import numpy as np
import multiprocessing as mp
import random
import argparse
import datetime
import logging

tf.compat.v1.enable_eager_execution()

LOGGER_NAME = "preprocess-goldfish"

# Globals duplicated in each process
OUTPUT_INFIX = f"{int(datetime.datetime.now().timestamp())}"
IN_MEMORY_FILES = None
OUTPUT_PREFIX = None
MAXIMUM_CLIP_LENGTH = None
LABEL_MAP = None


def get_length_filter(length: int) -> Callable[[tf.train.Example], bool]:
    def f(x: bytes):
        example = tf.train.Example.FromString(x)
        sample_rate = tfexample_utils.get_sample_rate(example)
        audio = tfexample_utils.get_audio(example)

        return (len(audio) / sample_rate) <= length

    return f


def get_audio_padding(length: int) -> Callable[[tf.train.Example], tf.train.Example]:
    def f(x: bytes):
        example = tf.train.Example.FromString(x)
        text = tfexample_utils.get_text(example)
        sample_rate = tfexample_utils.get_sample_rate(example)
        audio = tfexample_utils.get_audio(example)

        pad_to = int(sample_rate * length)

        padding = np.random.normal(0, 10, size=pad_to - len(audio)).astype(np.int64)

        audio.extend(padding)

        return tfexample_utils.create_example(text=text,
                                              sample_rate=sample_rate,
                                              audio=audio).SerializeToString()

    return f


def get_labler():
    global LABEL_MAP

    def f(x: bytes):
        example = tf.train.Example.FromString(x)

        text = tfexample_utils.get_text(example)
        sample_rate = tfexample_utils.get_sample_rate(example)
        audio = tfexample_utils.get_audio(example)

        if text in LABEL_MAP:
            label = LABEL_MAP[text]
        else:
            label = LABEL_MAP["[UNK]"]  # Unknown token

        return tfexample_utils.create_example(text=text,
                                              sample_rate=sample_rate,
                                              audio=audio,
                                              label=label).SerializeToString()

    return f


def create_jobs(file_path_prefix: str, processes: int):
    entries = file_path_prefix.split("/")

    path = "/".join(entries[:-1])
    prefix = entries[-1]

    files = pathlib.Path(path).glob(f"{prefix}")
    buckets = [[] for _ in range(processes)]
    for file in files:
        bucket_index = np.random.randint(0, processes)

        buckets[bucket_index].append(str(file))

    return buckets


def exec_job(job: (int, List[str])):
    id, job = job
    process_local_index = 0

    length_filter = get_length_filter(MAXIMUM_CLIP_LENGTH)
    padding = get_audio_padding(MAXIMUM_CLIP_LENGTH)
    labler = get_labler()

    dropped_audio_files = 0
    while job:
        load_in_memory = job[:IN_MEMORY_FILES]

        examples = []
        for example in tf.data.TFRecordDataset(filenames=load_in_memory):
            example = example.numpy()
            """ Apply pipeline functions here"""

            # If clip is too long drop it
            if not length_filter(example):
                dropped_audio_files += 1
                continue

            # Pads all clips to same length
            example = padding(example)

            # Adds labels to clips using label map
            example = labler(example)

            """ End of pipeline functions """
            examples.append(example)

        random.shuffle(examples)

        buckets = [examples[i::IN_MEMORY_FILES] for i in range(IN_MEMORY_FILES)]

        for bucket in buckets:
            str_id = str(process_local_index)
            padded_id = "0" * (5 - len(str_id)) + str_id
            sharded_file = f"{OUTPUT_PREFIX}-{OUTPUT_INFIX}-{id}-{padded_id}"
            with tf.io.TFRecordWriter(sharded_file) as writer:
                for example in bucket:
                    writer.write(example)

            process_local_index += 1

        job = job[IN_MEMORY_FILES:]

        logger.info(f"Dropped audio files {dropped_audio_files}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(LOGGER_NAME)

    parser = argparse.ArgumentParser()
    parser.add_argument("--source_prefix",
                        type=str,
                        help="Prefix of sharded file",
                        required=True)
    parser.add_argument("--output_path",
                        type=str,
                        help="Prefix of sharded output file",
                        required=True)
    parser.add_argument('--label_map_path', type=str, dest="label_map_path",
                        help="Path to json label map for labels", required=True)
    parser.add_argument('--maximum_clip_length', type=int, dest="maximum_clip_length",
                        help="All audio clips with length longer than 'maximum_clip_length' will be dropped",
                        default=2)
    parser.add_argument('--in_memory_files', type=int, dest="in_memory_files",
                        help="The number of files to load into memory at once -- more files gives better shuffling",
                        default=10)

    args = parser.parse_args()

    IN_MEMORY_FILES = args.in_memory_files
    OUTPUT_PREFIX = args.output_path
    MAXIMUM_CLIP_LENGTH = args.maximum_clip_length

    logger.info(f"In memory files: {IN_MEMORY_FILES}")
    logger.info(f"Output Prefix: {OUTPUT_PREFIX}")
    logger.info(f"Output Infix: {OUTPUT_INFIX}")
    logger.info(f"Maximum Clip Length: {MAXIMUM_CLIP_LENGTH}")

    label_map_path = pathlib.Path(args.label_map_path)
    if not label_map_path.is_file():
        logger.fatal(f"{label_map_path} is not a valid file")
        sys.exit(1)

    with open(label_map_path, "r") as json_label_map:
        LABEL_MAP = json.load(json_label_map)

    logger.info(f"Read label map from {label_map_path}")

    processes_to_use = np.maximum(mp.cpu_count() - 1, 1)
    jobs = create_jobs(args.source_prefix, processes_to_use)

    with mp.Pool() as pool:
        for _ in pool.imap_unordered(exec_job, list(enumerate(jobs)), 1):
            pass
