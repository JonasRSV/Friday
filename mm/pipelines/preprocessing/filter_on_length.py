import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
from pipelines.preprocessing.abstract_preprocess_fn import PreprocessFn
from typing import List


class LengthFilter(PreprocessFn):

    def __init__(self, max_length: float, min_length: float):
        self.max_length = max_length
        self.min_length = min_length

    def do(self, example: tf.train.Example) -> List[tf.train.Example]:
        sample_rate = tfexample_utils.get_sample_rate(example)
        audio = tfexample_utils.get_audio(example)

        if self.min_length <= (len(audio) / sample_rate) <= self.max_length:
            return [example]

        return []
