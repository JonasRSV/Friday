import tensorflow as tf
import numpy as np

def int64list_feature(value):
    """Returns an int64_list from a bool / enum / int / uint."""
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))


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
        sample_rate: int,
        anchor_audio: np.array,
        anchor_text: str,
        positive_audio: np.array,
        positive_text: str,
        negative_audio: np.array,
        negative_text: str) -> tf.train.Example:

    features = tf.train.Features(
        feature=dict(
            anchor=bytes_feature(
                np.array(anchor_audio, dtype=np.int16).tobytes()
            ),
            positive=bytes_feature(
                np.array(positive_audio, dtype=np.int16).tobytes()
            ),
            negative=bytes_feature(
                np.array(negative_audio, dtype=np.int16).tobytes()
            ),
            anchor_text=bytes_feature(
                anchor_text.encode("utf-8")
            ),
            positive_text=bytes_feature(
                positive_text.encode("utf-8")
            ),
            negative_text=bytes_feature(
                negative_text.encode("utf-8")
            ),
            sample_rate=int64list_feature([
                int(sample_rate)
            ])))

    return tf.train.Example(features=features)
