import tensorflow as tf
from typing import List


def get_utterances(example: tf.train.Example) -> str:
    return example.features.feature["utterances"].bytes_list.value[0].decode("utf-8")


def get_audio(example: tf.train.Example) -> List[int]:
    return example.features.feature["audio"].int64_list.value


def get_sample_rate(example: tf.train.Example) -> int:
    return example.features.feature["sample_rate"].int64_list.value[0]


def get_at_time(example: tf.train.Example) -> List[int]:
    return example.features.feature["at_time"].int64_list.value


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
