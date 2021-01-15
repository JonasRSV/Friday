import tensorflow as tf
from typing import List


def get_text(example: tf.train.Example) -> str:
    return example.features.feature["text"].bytes_list.value[0].decode("utf-8")


def set_text(example: tf.train.Example, text: str) -> tf.train.Example:
    example.features.feature["text"].bytes_list.value[0] = text.encode("utf-8")

    return example


def get_audio(example: tf.train.Example) -> [int]:
    return example.features.feature["audio"].int64_list.value


def set_audio(example: tf.train.Example, audio: [int]) -> tf.train.Example:
    if len(example.features.feature["audio"].int64_list.value) == len(audio):
        # If they are the same length we can just overwrite
        example.features.feature["audio"].int64_list.value[:] = audio
    else:
        # we first have to delete it then reassign it
        del example.features.feature["audio"].int64_list.value[:]
        example.features.feature["audio"].int64_list.value.extend(audio)

    return example


def get_sample_rate(example: tf.train.Example) -> int:
    return example.features.feature["sample_rate"].int64_list.value[0]


def set_sample_rate(example: tf.train.Example, sample_rate: int) -> tf.train.Example:
    example.features.feature["sample_rate"].int64_list.value[0] = sample_rate

    return example


def get_label(example: tf.train.Example) -> int:
    return example.features.feature["label"].int64_list.value[0]


def set_label(example: tf.train.Example, label: int) -> tf.train.Example:
    if "label" in example.features.feature:
        example.features.feature["label"].int64_list.value[0] = label
    else:
        example.features.feature["label"].int64_list.value.append(label)

    return example


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
