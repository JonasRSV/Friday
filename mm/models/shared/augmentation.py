from typing import List
import tensorflow as tf
import numpy as np
import models.shared.augmentations as a
import random


def randomly_apply_augmentations(sample_rate: int):
    def inject_noise(audio: tf.Tensor, level: int) -> tf.Tensor:
        return audio + tf.cast(tf.random.normal(shape=audio.shape, mean=0, stddev=level), tf.int16)

    def shift(audio: tf.Tensor, amount: int) -> tf.Tensor:
        return tf.roll(audio, shift=amount, axis=0)

    def mapping(example: tf.train.Example):
        random_number = tf.random.uniform(minval=0, maxval=1, shape=())

        example["audio"] = tf.case(
            [
                (tf.greater(0.1, random_number), lambda: inject_noise(example["audio"], level=10)),
                (tf.greater(0.2, random_number), lambda: inject_noise(example["audio"], level=50)),
                (tf.greater(0.3, random_number), lambda: inject_noise(example["audio"], level=100)),
                (tf.greater(0.4, random_number), lambda: inject_noise(example["audio"], level=200)),
                (tf.greater(0.5, random_number), lambda: shift(example["audio"], amount=200)),
                (tf.greater(0.6, random_number), lambda: shift(example["audio"], amount=-50)),
                (tf.greater(0.7, random_number), lambda: shift(inject_noise(example["audio"], level=200), 200)),
                (tf.greater(0.8, random_number), lambda: shift(inject_noise(example["audio"], level=150), 150)),
                (tf.greater(0.9, random_number), lambda: shift(inject_noise(example["audio"], level=130), 70)),
            ],
            default=lambda: example["audio"])

        return example

    return mapping


def create_audio_augmentations(aug: List[a.Augmentation], p: np.ndarray):
    if len(aug) != len(p):
        raise ValueError(f"Length of augmentations must match distribution {len(aug)} != {len(p)}")

    def audio_augmentations(audio: np.ndarray, sample_rate: int):
        for aug_to_apply, with_prob in zip(aug, p):
            if np.random.rand() < with_prob:
                audio = aug_to_apply.apply(audio, sample_rate)

        return audio

    return audio_augmentations
