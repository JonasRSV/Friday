import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
from pipelines.preprocessing.abstract_preprocess_fn import PreprocessFn
from typing import List


class TextLowerCase(PreprocessFn):

    def do(self, example: tf.train.Example) -> List[tf.train.Example]:
        text = tfexample_utils.get_text(example)
        text = text.lower()

        return [tfexample_utils.set_text(example=example, text=text)]
