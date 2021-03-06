import sys
import os

# Some systems dont use the launching directory as root
sys.path.append(os.getcwd())

import pathlib
from typing import List
import tensorflow as tf
import random
import argparse
from tqdm import tqdm

tf.compat.v1.enable_eager_execution()


def get_files_to_shuffle(source_prefix: str) -> List[pathlib.Path]:
    # e.g data/../tfexamples*
    p = source_prefix.split("/")
    base_path = "/".join(p[:-1])
    glob_prefix = p[-1]
    files = []
    for file in pathlib.Path(base_path).glob(glob_prefix):
        if file.is_file():
            files.append(file)
    return files


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--source",
                        type=str,
                        help="Prefix of sharded file",
                        required=True)

    args = parser.parse_args()

    files = get_files_to_shuffle(args.source)

    # This only does 'within file' shuffling, the 'across file' shuffling is done by the preprocess.py file
    with tqdm(total=len(files)) as progress_bar:
        for file in files:
            examples = [example.numpy() for example in tf.data.TFRecordDataset(filenames=[str(file)])]
            random.shuffle(examples)

            with tf.io.TFRecordWriter(str(file)) as writer:
                for example in examples:
                    writer.write(example)

            progress_bar.update()
