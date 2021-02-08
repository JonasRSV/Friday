import sys
import os

# Some systems dont use the launching directory as root
sys.path.append(os.getcwd())

import pathlib
import shared.tfexample_utils as tfexample_utils
import sox
from typing import List
import tensorflow as tf
import argparse
import random
from tqdm import tqdm

tf.compat.v1.enable_eager_execution()


class Job:
    def __init__(self, keyword: str, path: pathlib.Path):
        self.keyword = keyword
        self.path = path

    def exec(self, writer: tf.io.TFRecordWriter, sample_rate: int):
        transformer = sox.Transformer()
        transformer.set_output_format(rate=sample_rate, channels=1)
        resampled_audio = transformer.build_array(
            input_filepath=str(self.path), sample_rate_in=sample_rate)

        example = tfexample_utils.create_example(
            audio=resampled_audio,
            text=self.keyword,
            sample_rate=sample_rate
        )

        writer.write(example.SerializeToString())


def build_jobs(source_directory: str) -> List[Job]:
    source_directory = pathlib.Path(source_directory)
    if not source_directory.is_dir():
        raise ValueError(f"{source_directory} is not a valid directory")

    jobs = []
    for path in pathlib.Path(source_directory).glob("*"):
        file_name = path.stem
        keyword = file_name.split("-")[0].replace("_", " ")
        jobs.append(Job(keyword=keyword, path=path))

    return jobs


BASE = "abcdefghijklmnopqrstuvxyz1234567890"


def random_base_part(k):
    return "".join(random.choices(BASE, k=k))


def get_uuid() -> str:
    return f"{random_base_part(5)}-{random_base_part(5)}-{random_base_part(5)}-{random_base_part(5)}"


def get_next_sink_prefix(sink: str):
    return f"{sink}/tfexamples.recordyourownwesite.{get_uuid()}"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--source",
                        type=str,
                        help="Prefix of sharded file",
                        required=True)
    parser.add_argument("--sink",
                        type=str,
                        help="output directory",
                        required=True)
    parser.add_argument("--sample_rate",
                        type=int,
                        help="Sample-rate to resample too",
                        default=8000)

    args = parser.parse_args()

    jobs = build_jobs(args.source)

    writer = tf.io.TFRecordWriter(get_next_sink_prefix(args.sink))
    for i, job in enumerate(tqdm(jobs), 1):
        if i % 250 == 0:
            writer.flush()
            writer.close()
            writer = tf.io.TFRecordWriter(get_next_sink_prefix(args.sink))

        try:
            job.exec(writer, args.sample_rate)
        except Exception as e:
            print(f"Failed on {job.path}.. ignoring, reason: {e}")

