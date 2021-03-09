import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
import numpy as np
from pipelines.preprocessing.abstract_preprocess_fn import PreprocessFn
from typing import List


class RandomBiPadding(PreprocessFn):
    """Pads both sides such that the length becomes 'length'. But pads randomly"""

    def __init__(self, length: float):
        self.length = length

    def do(self, example: tf.train.Example) -> List[tf.train.Example]:
        sample_rate = tfexample_utils.get_sample_rate(example)
        audio = tfexample_utils.get_audio(example)

        pad_to = int(sample_rate * self.length)
        num_padding = pad_to - len(audio)

        padding = list(np.random.normal(0, 10, size=num_padding).astype(np.int64))

        padding_split = np.random.randint(0, num_padding)

        head_padding = padding[:padding_split]
        tail_padding = padding[padding_split:]

        head_padding.extend(audio)
        head_padding.extend(tail_padding)

        return [tfexample_utils.set_audio(example=example, audio=head_padding)]
