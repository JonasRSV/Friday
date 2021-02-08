import pathlib
import tensorflow as tf
import random
import os
from pipelines.preprocessing.abstract_preprocess_fn import PreprocessFn
from typing import List, Iterable


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
