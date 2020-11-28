import pathlib
import tensorflow as tf
import random
import argparse
import logging
from tqdm import tqdm

tf.compat.v1.enable_eager_execution()

LOGGER_NAME = "TrainValidSplit"


def run_split(source_prefix: str, sink_prefix: str, examples_per_shard: int, train_fraction: float):
    entries = source_prefix.split("/")
    path = "/".join(entries[:-1])
    prefix = entries[-1]

    files = list(pathlib.Path(path).glob(f"{prefix}"))

    train_index = 0
    valid_index = 0

    def next_train_file():
        nonlocal train_index, sink_prefix
        padding = 5 - len(str(train_index))

        file_name = f"{sink_prefix}.train-{'0' * padding}{train_index}"
        train_index += 1
        return file_name

    def next_valid_file():
        nonlocal valid_index, sink_prefix
        padding = 5 - len(str(valid_index))

        file_name = f"{sink_prefix}.valid-{'0' * padding}{valid_index}"
        valid_index += 1
        return file_name

    train_file_entries = 0
    valid_file_entries = 0

    train_file_writer = tf.io.TFRecordWriter(next_train_file())
    valid_file_writer = tf.io.TFRecordWriter(next_valid_file())

    total_train = 0
    total_valid = 0
    for file in tqdm(files):
        for example in tf.data.TFRecordDataset(filenames=[str(file)]):
            example = example.numpy()

            if random.random() < train_fraction:
                total_train += 1

                train_file_entries += 1
                train_file_writer.write(example)
            else:
                total_valid += 1

                valid_file_entries += 1
                valid_file_writer.write(example)

            if train_file_entries >= examples_per_shard:
                train_file_entries = 0
                train_file_writer.close()

                train_file_writer = tf.io.TFRecordWriter(next_train_file())

            if valid_file_entries >= examples_per_shard:
                valid_file_entries = 0
                valid_file_writer.close()

                valid_file_writer = tf.io.TFRecordWriter(next_valid_file())

    train_file_writer.close()
    valid_file_writer.close()

    logger.info(f"train_examples: {total_train} -- valid_examples: {total_valid}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(LOGGER_NAME)

    parser = argparse.ArgumentParser()
    parser.add_argument("--source_prefix",
                        type=str,
                        help="Prefix of sharded file",
                        required=True)
    parser.add_argument("--sink_prefix",
                        type=str,
                        help="Prefix of sharded output file",
                        required=True)
    parser.add_argument('--examples_per_shard', type=int, dest="examples_per_shard",
                        help="Number of examples to store per shard",
                        default=100)
    parser.add_argument('--train_fraction', type=float, dest="train_fraction",
                        help="fraction of data to train on",
                        default=0.8)

    args = parser.parse_args()
    logger.info(f"Source Prefix: {args.source_prefix}")
    logger.info(f"Sink Prefix: {args.sink_prefix}")
    logger.info(f"Examples per shard: {args.examples_per_shard}")
    logger.info(f"Train fraction: {args.train_fraction}")

    run_split(source_prefix=args.source_prefix, sink_prefix=args.sink_prefix,
              examples_per_shard=args.examples_per_shard,
              train_fraction=args.train_fraction)
