import simpleaudio
import tensorflow as tf
import argparse
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import random
from enum import Enum
from tqdm import tqdm

import shared.tfexample_utils as tfexample_utils

tf.compat.v1.enable_eager_execution()


class InvalidFileError(Exception):
    """"""
    pass


class Mode(Enum):
    play_audio = "play_audio"
    visualize = "visualize"
    meta = "meta"
    count_labels = "count_labels"
    play_random = "play_random"


def play_audio(file: str, *_):
    # TODO(jonasrsv): support for sharding and advanced choice

    file_path = pathlib.Path(file)

    if not file_path.is_file():
        raise InvalidFileError(f"{file} is not a valid file")

    dataset = tf.data.TFRecordDataset([file])
    for serialized_example in dataset.take(100):
        example = tf.train.Example()
        example.ParseFromString(serialized_example.numpy())

        audio = np.array(tfexample_utils.get_audio(example), dtype=np.int16)
        sample_rate = tfexample_utils.get_sample_rate(example)

        simpleaudio.play_buffer(audio, 1, 2,
                                sample_rate=sample_rate).wait_done()


def visualize(file: str, *_):
    file_path = pathlib.Path(file)

    if not file_path.is_file():
        raise InvalidFileError(f"{file} is not a valid file")

    dataset = tf.data.TFRecordDataset([file])
    for i, serialized_example in enumerate(dataset.take(5), 1):
        example = tf.train.Example()
        example.ParseFromString(serialized_example.numpy())

        audio = np.array(tfexample_utils.get_audio(example), dtype=np.int16)
        text = tfexample_utils.get_text(example)

        plt.subplot(5, 1, i)
        plt.title(f"{text}")
        x = np.arange(audio.size)
        y = audio
        plt.plot(x, y)

    plt.tight_layout()
    plt.show()


def show_meta(file: str, *_):
    file_path = pathlib.Path(file)

    if not file_path.is_file():
        raise InvalidFileError(f"{file} is not a valid file")

    dataset = tf.data.TFRecordDataset([file])
    for i, serialized_example in enumerate(dataset, 1):
        example = tf.train.Example()
        example.ParseFromString(serialized_example.numpy())

        text = tfexample_utils.get_text(example)
        sample_rate = tfexample_utils.get_sample_rate(example)
        audio = tfexample_utils.get_audio(example)

        label = None
        try:
            label = tfexample_utils.get_label(example)
        except IndexError:
            pass

        print(f"len(audio): {len(audio)}\ntext: {text}\nsample_rate: {sample_rate}\nlabel: {label}\n\n")


def count_labels(path: str, *_):
    entries = path.split("/")

    path = "/".join(entries[:-1])
    prefix = entries[-1]

    files = list(pathlib.Path(path).glob(f"{prefix}"))

    text_counts = {}
    for file in tqdm(files):
        for example in tf.data.TFRecordDataset(filenames=[str(file)]):
            example = example.numpy()
            example = tf.train.Example.FromString(example)
            text = tfexample_utils.get_text(example)
            label = None
            try:
                label = tfexample_utils.get_label(example)
            except IndexError:
                pass

            if text not in text_counts:
                text_counts[text] = {
                    'counts': 0,
                    'label_counts': 0
                }

            text_counts[text]['counts'] += 1
            text_counts[text]['label_counts'] += 1 if label is not None else 0

    tuples = [(v['counts'], v['label_counts'], k) for k, v in text_counts.items()]
    tuples.sort()

    for counts, label_counts, k, in tuples:
        print(f"{k}: {counts} -- label counts: {label_counts}")


def play_random(path: str, name: str):
    entries = path.split("/")

    path = "/".join(entries[:-1])
    prefix = entries[-1]

    files = list(pathlib.Path(path).glob(f"{prefix}"))
    random.shuffle(files)

    for file in tqdm(files):
        for example in tf.data.TFRecordDataset(filenames=[str(file)]):
            example = example.numpy()
            example = tf.train.Example.FromString(example)

            text = tfexample_utils.get_text(example)
            if text == name and random.random() < 0.5:
                label = None
                try:
                    label = tfexample_utils.get_label(example)
                except IndexError:
                    pass
                audio = np.array(tfexample_utils.get_audio(example), dtype=np.int16)
                sample_rate = tfexample_utils.get_sample_rate(example)

                print(f"Playing {text} -- label: {label}")
                simpleaudio.play_buffer(audio, 1, 2,
                                        sample_rate=sample_rate).wait_done()

                return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path",
                        type=str,
                        help="Path to goldfish audio file / prefix",
                        required=True)
    parser.add_argument("--mode", type=Mode, choices=list(Mode), required=True)
    parser.add_argument("--arg",
                        type=str,
                        help="")

    args = parser.parse_args()

    mode = {Mode.play_audio: play_audio,
            Mode.visualize: visualize,
            Mode.meta: show_meta,
            Mode.count_labels: count_labels,
            Mode.play_random: play_random
            }

    mode[args.mode](args.path, args.arg)
