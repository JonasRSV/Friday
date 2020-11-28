import tensorflow as tf
from typing import List


def get_text(example: tf.train.Example):
    return example.features.feature["text"].bytes_list.value[0].decode("utf-8")


def get_audio(example: tf.train.Example):
    return example.features.feature["audio"].int64_list.value


def get_sample_rate(example: tf.train.Example):
    return example.features.feature["sample_rate"].int64_list.value[0]


def get_label(example: tf.train.Example):
    return example.features.feature["label"].int64_list.value[0]


def bytes_feature(value):
    """Returns a bytes_list from a string / byte."""
    if isinstance(value, type(tf.constant(0))):
        value = value.numpy(
        )  # BytesList won't unpack a string from an EagerTensor.
    return tf.train.Feature(bytes_list=tf.train.BytesList(
        value=[value.encode("utf-8")]))


def int64list_feature(value):
    """Returns an int64_list from a bool / enum / int / uint."""
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))


def create_example(
        text: str,
        audio: List[int],
        sample_rate: int,
        label: int = None) -> tf.train.Example:

    if label is not None:
        features = tf.train.Features(
            feature=dict(audio=int64list_feature(audio),
                         text=bytes_feature(text),
                         sample_rate=int64list_feature([sample_rate]),
                         label=int64list_feature([label])))
    else:
        features = tf.train.Features(
            feature=dict(audio=int64list_feature(audio),
                         text=bytes_feature(text),
                         sample_rate=int64list_feature([sample_rate])))

    return tf.train.Example(features=features)
