import sys
import os

# Some systems dont use the launching directory as root
sys.path.append(os.getcwd())

import pathlib
import json
from typing import List, Iterable
import tensorflow as tf
import multiprocessing as mp
import random
import argparse
from pipelines.preprocessing.abstract_preprocess_fn import PreprocessFn
from pipelines.preprocessing.audio_padding import AudioPadding
from pipelines.preprocessing.filter_on_length import LengthFilter
from pipelines.preprocessing.label_map_labler import Labler
from tqdm import tqdm

tf.compat.v1.enable_eager_execution()


class Job:
    # Each input file gets its own job
    def __init__(self):
        self.doFns = None
        self.file = None
        self.size = None

        self.sinks = None

    def add_file_information(self, file: pathlib.Path, size: float):
        self.file = file
        self.size = size

        return self

    def add_preprocessing_fn(self, doFns: List[PreprocessFn]):
        self.doFns = doFns

        return self

    def add_sinks(self, sinks: List[tf.io.TFRecordWriter]):
        self.sinks = sinks

        return self

    def execute(self):
        for example in tf.data.TFRecordDataset(filenames=[str(self.file)]):
            example = example.numpy()
            """ Apply pipeline functions here"""
            example = tf.train.Example.FromString(example)

            dofn_r = [example]
            for dofn in self.doFns:
                lr = []
                for ex in dofn_r:
                    lr.extend(dofn.do(ex))

                dofn_r = lr

            for ex in dofn_r:
                random_sink = random.choice(self.sinks)
                random_sink.write(ex.SerializeToString())


def build_jobs_with_file_information(source_prefix: str) -> (Iterable[Job], float):
    # e.g data/../tfexamples*
    p = source_prefix.split("/")
    base_path = "/".join(p[:-1])
    glob_prefix = p[-1]
    amount_of_data_to_preprocess = 0.0
    jobs = []
    for file in pathlib.Path(base_path).glob(glob_prefix):
        if file.is_file():
            jobs.append(Job().add_file_information(file=file, size=os.path.getsize(str(file)) / 1e6))
            amount_of_data_to_preprocess += jobs[-1].size
    print(f"Total amount of data to preprocess: {amount_of_data_to_preprocess} MB")
    return jobs, amount_of_data_to_preprocess


def create_sinks(prefix: str, n: int) -> List[tf.io.TFRecordWriter]:
    sinks = []
    for i in range(n):
        str_id = str(i)
        padded_id = "0" * (5 - len(str_id)) + str_id
        sharded_file = f"{prefix}-{padded_id}"
        sinks.append(tf.io.TFRecordWriter(sharded_file))
    return sinks


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--source",
                        type=str,
                        help="Prefix of sharded file",
                        required=True)
    parser.add_argument("--sink_prefix",
                        type=str,
                        help="Prefix of output sharded file",
                        required=True)
    parser.add_argument('--label_map_path', type=str, dest="label_map_path",
                        help="Path to json label map for labels", required=True)
    parser.add_argument('--maximum_clip_length', type=int, dest="maximum_clip_length",
                        help="All audio clips with length longer than 'maximum_clip_length' will be dropped",
                        default=2)

    args = parser.parse_args()

    with open(args.label_map_path, "r") as label_map_file:
        doFns = [
            LengthFilter(max_length=args.maximum_clip_length, min_length=0.0),
            AudioPadding(length=args.maximum_clip_length),
            Labler(label_map=json.load(label_map_file)),
        ]

    jobs, memory_to_process = build_jobs_with_file_information(source_prefix=args.source)

    expected_MB_per_file = 100
    sinks = create_sinks(prefix=args.sink_prefix, n=int(memory_to_process / expected_MB_per_file))
    jobs = [job.add_preprocessing_fn(doFns=doFns).add_sinks(sinks) for job in jobs]

    with tqdm(total=memory_to_process) as progress_bar:
        # TODO look into creating some kind of custom lock so we can run this across multiple processes
        # The current problem is that by naively multiprocessing this we will run into race conditions when writing
        # to file. Also it is unclear if the tensorflow writers can be pickled and used with python MP.
        # Need to figure out what the bottleneck is, perhaps it is IO and in that case threading might be enough.
        for job in jobs:
            job.execute()
            progress_bar.update(n=job.size)