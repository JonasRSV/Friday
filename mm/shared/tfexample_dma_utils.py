import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
import numpy as np


def get_anchor_text(example: tf.train.Example) -> str:
    return example.features.feature["anchor_text"].bytes_list.value[0].decode("utf-8")


def get_positive_text(example: tf.train.Example) -> str:
    return example.features.feature["positive_text"].bytes_list.value[0].decode("utf-8")


def get_negative_text(example: tf.train.Example) -> str:
    return example.features.feature["negative_text"].bytes_list.value[0].decode("utf-8")


def get_anchor_audio(example: tf.train.Example) -> np.array:
    return np.fromstring(example.features.feature["anchor"].bytes_list.value[0], dtype=np.int16)


def get_positive_audio(example: tf.train.Example) -> [int]:
    return np.fromstring(example.features.feature["positive"].bytes_list.value[0], dtype=np.int16)


def get_negative_audio(example: tf.train.Example) -> [int]:
    return np.fromstring(example.features.feature["negative"].bytes_list.value[0], dtype=np.int16)


def get_sample_rate(example: tf.train.Example) -> int:
    return example.features.feature["sample_rate"].int64_list.value[0]


def bytes_feature(value):
    """Returns a bytes_list from a string / byte."""
    return tf.train.Feature(bytes_list=tf.train.BytesList(
        value=[value]))


def create_example(
        anchor: tf.train.Example,
        positive: tf.train.Example,
        negative: tf.train.Example) -> tf.train.Example:
    assert tfexample_utils.get_sample_rate(anchor) == tfexample_utils.get_sample_rate(positive) \
           == tfexample_utils.get_sample_rate(negative)

    features = tf.train.Features(
        feature=dict(
            anchor=bytes_feature(
                np.array(tfexample_utils.get_audio(anchor), dtype=np.int16).tobytes()
            ),
            positive=bytes_feature(
                np.array(tfexample_utils.get_audio(positive), dtype=np.int16).tobytes()
            ),
            negative=bytes_feature(
                np.array(tfexample_utils.get_audio(negative), dtype=np.int16).tobytes()
            ),
            anchor_text=tfexample_utils.bytes_feature(
                tfexample_utils.get_text(anchor)
            ),
            positive_text=tfexample_utils.bytes_feature(
                tfexample_utils.get_text(positive)
            ),
            negative_text=tfexample_utils.bytes_feature(
                tfexample_utils.get_text(negative)
            ),
            sample_rate=tfexample_utils.int64list_feature([
                tfexample_utils.get_sample_rate(positive)
            ])))

    return tf.train.Example(features=features)
