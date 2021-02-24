import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
from pipelines.preprocessing.abstract_preprocess_fn import PreprocessFn
from typing import List


class Chunker(PreprocessFn):
    """Function for chunking long audio clips into smaller audio clips."""

    def __init__(self, max_clip_length: float, chunk_stride: float):
        """Chunk clips into at most 'max_clip_length'."""
        self.max_clip_length = max_clip_length
        self.chunk_stride = chunk_stride

    def do(self, example: tf.train.Example) -> List[tf.train.Example]:
        sample_rate = tfexample_utils.get_sample_rate(example)
        audio = tfexample_utils.get_audio(example)

        max_samples = int(sample_rate * self.max_clip_length)
        stride = int(sample_rate * self.chunk_stride)

        # If audio does not need chunking we do early return.
        if len(audio) <= max_samples:
            return [example]

        examples, current_sample = [], 0
        while current_sample + max_samples < len(audio):
            examples.append(
                tfexample_utils.create_example(
                    text="",
                    audio=audio[current_sample: current_sample + max_samples],
                    sample_rate=sample_rate
                )
            )

            current_sample += stride

        # TODO(jonasrsv): Add final chunk or not?

        return examples
