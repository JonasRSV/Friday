import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
import numpy as np
from pipelines.preprocessing.abstract_preprocess_fn import PreprocessFn
from typing import List


class AudioPadding(PreprocessFn):

    def __init__(self, length: float):
        self.length = length

    def do(self, example: tf.train.Example) -> List[tf.train.Example]:
        sample_rate = tfexample_utils.get_sample_rate(example)
        audio = tfexample_utils.get_audio(example)

        pad_to = int(sample_rate * self.length)
        padding = np.random.normal(0, 10, size=pad_to - len(audio)).astype(np.int64)

        audio.extend(padding)

        return [tfexample_utils.set_audio(example=example, audio=audio)]
