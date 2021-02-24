import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
from pipelines.preprocessing.abstract_preprocess_fn import PreprocessFn
from typing import List


class HashLabeler(PreprocessFn):
    """Function for adding a hash label to our audio files.

    Instead of actually hashing we just add a counter, this guarantees no collisions. The counter approach will
    work as long as we can keep all of the unique text string in memory: which will be possible for the forseeable
    future.

    Audio files which contains empty text will get the '0' label.
    """

    def __init__(self):
        """Chunk clips into at most 'max_clip_length'."""
        # 0 is reserved for 'unknown'
        # Counter starts with the smallest number representable with a int64
        self.counter = -(2 ** 63 - 1)
        self.seen_texts = {}

    def increment_counter(self):
        self.counter += 1

        if self.counter == 0:
            self.increment_counter()

    def do(self, example: tf.train.Example) -> List[tf.train.Example]:
        text = tfexample_utils.get_text(example)

        if text:
            if text not in self.seen_texts:
                self.seen_texts[text] = self.counter
                self.increment_counter()

            return [tfexample_utils.set_label(example=example,
                                              label=self.seen_texts[text])]

        return [tfexample_utils.set_label(example=example,
                                          label=0)]
