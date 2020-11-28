import warnings

warnings.filterwarnings("ignore")
import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
import numpy as np
import multiprocessing as mp
import argparse
import pathlib
import pandas as pd
import datetime
import logging
import sox
from typing import List
from tqdm import tqdm

OUTPUT_INFIX = f"{int(datetime.datetime.now().timestamp())}"
OUTPUT_PREFIX = None
SAMPLE_RATE = None


class InvalidFileError(Exception):
    """"""
    pass


class InvalidDirectoryError(Exception):
    """"""
    pass


def _bytes_feature(value):
    """Returns a bytes_list from a string / byte."""
    if isinstance(value, type(tf.constant(0))):
        value = value.numpy(
        )  # BytesList won't unpack a string from an EagerTensor.
    return tf.train.Feature(bytes_list=tf.train.BytesList(
        value=[value.encode("utf-8")]))


def _int64list_feature(value):
    """Returns an int64_list from a bool / enum / int / uint."""
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))


class Job:
    def __init__(self, id: int, audio_files: List[str],
                 sentences: List[str]):
        self.id: int = id
        self.audio_files: List[str] = audio_files
        self.sentences: List[str] = sentences


def get_jobs(tsv_df: pd.DataFrame,
             clips_path: pathlib.Path,
             files_per_job: int = 1000):
    clips_path = str(clips_path)

    files = 0
    id = 0
    jobs, audio_files, sentences = [], [], []
    for index, (file_name, sentence) in tqdm(
            enumerate(zip(tsv_df["path"], tsv_df["sentence"]), 1)):

        files += 1
        audio_files.append(f"{clips_path}/{file_name}")
        sentences.append(sentence)

        if (index % files_per_job) == 0:
            jobs.append(
                Job(id=id,
                    audio_files=audio_files,
                    sentences=sentences))

            audio_files, sentences = [], []
            id += 1

    print("Total number of audio files", files)

    return jobs


def worker(job: Job):
    str_id = str(job.id)
    padded_id = "0" * (5 - len(str_id)) + str_id
    sharded_file = f"{OUTPUT_PREFIX}-{OUTPUT_INFIX}-{padded_id}"

    transformer = sox.Transformer()
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


def main(tsv: str, clips: str):
    tsv_path: pathlib.Path = pathlib.Path(tsv)
    clips_path: pathlib.Path = pathlib.Path(clips)

    if not tsv_path.is_file():
        raise InvalidFileError(f"Unable to identify {tsv} as a file")

    if not clips_path.is_dir():
        raise InvalidDirectoryError(
            f"Unable to identify {clips} as a directory")

    tsv_df = pd.read_csv(tsv, sep="\t")
    logging.info("Prepairing jobs")
    jobs = get_jobs(tsv_df, clips_path)
    logging.info(f"Running {len(jobs)} jobs")

    with mp.Pool(np.maximum(mp.cpu_count() - 2, 1)) as pool:
        list(tqdm(pool.imap_unordered(worker, jobs, 1)))

    logging.info("Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tsv",
                        type=str,
                        help="Path to tsv file containing file clip IDs",
                        required=True)
    parser.add_argument("--clips",
                        type=str,
                        help="Path to directory containing clips",
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

    main(args.tsv, args.clips)
