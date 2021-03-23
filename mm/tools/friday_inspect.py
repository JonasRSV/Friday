import sys
import os

# Some systems dont use the launching directory as root
sys.path.append(os.getcwd())

import models.shared.augmentation as augmentation
import models.shared.augmentations as a
import simpleaudio
import tensorflow as tf
import argparse
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import random
from enum import Enum
from tqdm import tqdm
import librosa
import seaborn as sb

import shared.tfexample_utils as tfexample_utils

tf.compat.v1.enable_eager_execution()


class InvalidFileError(Exception):
    """"""
    pass


class Mode(Enum):
    play_audio = "play_audio"
    play_augmented_audio = "play_augmented_audio"
    visualize = "visualize"
    meta = "meta"
    count_labels = "count_labels"
    play_random = "play_random"
    sequence_lengths = "sequence_lengths"


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

        print("playing..")
        simpleaudio.play_buffer(audio, 1, 2,
                                sample_rate=sample_rate).wait_done()


def play_audio_with_augmentation(file: str, *_):
    # TODO(jonasrsv): support for sharding and advanced choice

    file_path = pathlib.Path(file)

    if not file_path.is_file():
        raise InvalidFileError(f"{file} is not a valid file")

    augmenter = augmentation.create_audio_augmentations([
        #a.TimeStretch(min_rate=0.93, max_rate=0.98),
        #a.PitchShift(min_semitones=-1, max_semitones=1),
        #a.Shift(min_rate=-500, max_rate=500),
        a.Gain(min_gain=0.7, max_gain=1.3),
        a.Background(background_noises=pathlib.Path(f"{os.getenv('FRIDAY_DATA', default='data')}/background_noise"),
                     sample_rate=8000,
                     min_voice_factor=0.5,
                     max_voice_factor=0.8),
        a.GaussianNoise(loc=0, stddev=100)
    ],
        p=[
            #0.5,
            0.5,
            #0.3,
            0.1,
            0.8,
            0.2
           ]
    )

    dataset = tf.data.TFRecordDataset([file])
    for serialized_example in dataset.take(100):
        example = tf.train.Example()
        example.ParseFromString(serialized_example.numpy())

        sample_rate = tfexample_utils.get_sample_rate(example)
        audio = np.array(tfexample_utils.get_audio(example))

        audio = augmenter(audio, sample_rate)
        audio = np.array(audio, dtype=np.int16)

        print(audio.shape)
        simpleaudio.play_buffer(audio, 1, 2,
                                sample_rate=sample_rate).wait_done()


def visualize(file: str, *_):
    file_path = pathlib.Path(file)

    if not file_path.is_file():
        raise InvalidFileError(f"{file} is not a valid file")

    N_PLOTS = 5
    dataset = tf.data.TFRecordDataset([file])
    plt.figure(figsize=(10, 20))
    for i, serialized_example in enumerate(dataset.take(N_PLOTS)):
        example = tf.train.Example()
        example.ParseFromString(serialized_example.numpy())

        sample_rate = tfexample_utils.get_sample_rate(example)
        audio = np.array(tfexample_utils.get_audio(example), dtype=np.int16)
        text = tfexample_utils.get_text(example)

        # Plot raw signal
        plt.subplot(5, 3, 1 + 3 * i)
        plt.title(f"{text}")
        x = np.arange(audio.size)
        y = audio
        plt.plot(x, y)
        plt.subplot(5, 3, 2 + 3 * i)
        # Plot MFCC
        plt.title(f"{text}")
        float_audio = audio.astype(np.float64) / 32768.0
        feature = librosa.feature.mfcc(float_audio, sr=sample_rate,
                                       n_mfcc=40,
                                       n_fft=1024,
                                       hop_length=512,
                                       win_length=1024,
                                       n_mels=80)

        # feature = librosa.feature.mfcc(float_audio, sr=sample_rate, n_mfcc=40)

        sb.heatmap(feature)
        plt.subplot(5, 3, 3 + 3 * i)
        plt.title(f"{text}")
        feature = librosa.feature.melspectrogram(float_audio, sr=sample_rate)

        print("min Feature", feature.min())
        print("max Feature", feature.max())
        print("mean Feature", feature.max())
        print("std Feature", feature.std())
        sb.heatmap(feature)

        # Plot spectrogram

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
            label = tfexample_utils.get_phoneme_labels(example)
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


def sequence_lengths(path: str, *_):
    entries = path.split("/")

    path = "/".join(entries[:-1])
    prefix = entries[-1]

    files = list(pathlib.Path(path).glob(f"{prefix}"))

    max_audio_length = 0
    max_labels_length = 0
    for file in tqdm(files):
        for example in tf.data.TFRecordDataset(filenames=[str(file)]):
            example = example.numpy()
            example = tf.train.Example.FromString(example)

            phonemes = tfexample_utils.get_phoneme_labels(example)
            audio = tfexample_utils.get_audio(example)

            max_audio_length = max(len(audio), max_audio_length)
            max_labels_length = max(len(phonemes), max_labels_length)

    print(max_audio_length, max_labels_length)


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
            Mode.play_random: play_random,
            Mode.play_augmented_audio: play_audio_with_augmentation,
            Mode.sequence_lengths: sequence_lengths
            }

    mode[args.mode](args.path, args.arg)
