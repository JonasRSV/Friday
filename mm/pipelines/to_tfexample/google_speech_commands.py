import warnings
import sys
import os

# Some systems don't use the launching directory as root
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

warnings.filterwarnings("ignore")
import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
import numpy as np
import multiprocessing as mp
import argparse
import pathlib
import datetime
import logging
import sox
from typing import List
from tqdm import tqdm

OUTPUT_INFIX = f"{int(datetime.datetime.now().timestamp())}"
OUTPUT_PREFIX = None
SAMPLE_RATE = None

SUB_PATHS = [
    "backward",
    "bed",
    "bird",
    "cat",
    "dog",
    "down",
    "eight",
    "five",
    "follow",
    "forward",
    "four",
    "go",
    "happy",
    "house",
    "learn",
    "left",
    "marvin",
    "nine",
    "no",
    "off",
    "on",
    "one",
    "right",
    "seven",
    "sheila",
    "six",
    "stop",
    "three",
    "tree",
    "two",
    "up",
    "visual",
    "wow",
    "yes",
    "zero"
]


class InvalidDirectoryError(Exception):
    """"""
    pass


class Job:
    def __init__(self, id: int, audio_files: List[str],
                 sentences: List[str]):
        self.id: int = id
        self.audio_files: List[str] = audio_files
        self.sentences: List[str] = sentences


def get_jobs(base_path: pathlib.Path,
             sub_paths: List[str],
             files_per_job: int = 1000):
    id, job_id = 1, 1
    jobs, audio_files, sentences = [], [], []
    for s_path in sub_paths:

        path = base_path / s_path
        for file in path.glob("*"):
            audio_files.append(str(file))
            sentences.append(s_path)

            if id % files_per_job == 0:
                jobs.append(
                    Job(id=job_id,
                        audio_files=audio_files,
                        sentences=sentences))

                job_id += 1
                audio_files, sentences = [], []

            id += 1

        jobs.append(
            Job(id=job_id,
                audio_files=audio_files,
                sentences=sentences))

        job_id += 1
        # Jobs contains only 1 type of keyword
        audio_files, sentences = [], []

    # Not using logger here because the sox library is cluttering the info logging, need to mute that somehow
    print(f"Total number of audio files: {id - 1}")

    return jobs


def worker(job: Job):
    str_id = str(job.id)
    padded_id = "0" * (5 - len(str_id)) + str_id
    sharded_file = f"{OUTPUT_PREFIX}-{job.sentences[0]}-{OUTPUT_INFIX}-{padded_id}"

    transformer = sox.Transformer()
    transformer.set_output_format(rate=SAMPLE_RATE, channels=1)
    with tf.io.TFRecordWriter(sharded_file) as writer:
        for audio_file, sentence in zip(job.audio_files, job.sentences):
            resampled_audio = transformer.build_array(
                input_filepath=audio_file, sample_rate_in=SAMPLE_RATE)

            example = tfexample_utils.create_example(
                audio=resampled_audio,
                text=sentence,
                sample_rate=SAMPLE_RATE
            )

            writer.write(example.SerializeToString())


def main(base_path: pathlib.Path):
    if not base_path.is_dir():
        raise InvalidDirectoryError(
            f"Unable to identify {base_path} as a directory")

    """Validate that each subpath exists"""
    for path in SUB_PATHS:
        path = base_path / path

        if not path.is_dir():
            raise InvalidDirectoryError(
                f"Unable to identify {str(path)} as a directory -- please make sure it exists or remove it from subpaths")

    logging.info("Prepairing jobs")
    jobs = get_jobs(base_path, SUB_PATHS)
    logging.info(f"Running {len(jobs)} jobs")

    with tqdm(total=len(jobs)) as progress_bar:
        with mp.Pool(np.maximum(mp.cpu_count() - 2, 1)) as pool:
            for _ in pool.imap_unordered(worker, jobs, 1):
                progress_bar.update()

    logging.info("Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--base_path",
                        type=str,
                        help="Path to tsv file containing file clip IDs",
                        required=True)
    parser.add_argument("--output_prefix",
                        type=str,
                        help="Prefix of sharded output file",
                        required=True)
    parser.add_argument("--sample_rate",
                        type=int,
                        help="Sample rate to re-sample too",
                        default=8000)

    args = parser.parse_args()

    OUTPUT_PREFIX = args.output_prefix
    SAMPLE_RATE = args.sample_rate

    main(pathlib.Path(args.base_path))
