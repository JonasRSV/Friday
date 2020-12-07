import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
from pipelines.preprocessing.abstract_preprocess_fn import PreprocessFn
from typing import List, Mapping


class Labler(PreprocessFn):

    def __init__(self, label_map: Mapping[str, int]):
        self.label_map = label_map

    def do(self, example: tf.train.Example) -> List[tf.train.Example]:
        text = tfexample_utils.get_text(example)
        sample_rate = tfexample_utils.get_sample_rate(example)
        audio = tfexample_utils.get_audio(example)

        if text in self.label_map:
            label = self.label_map[text]
        else:
            label = self.label_map["[UNK]"]

        return [tfexample_utils.create_example(text=text,
                                               sample_rate=sample_rate,
                                               audio=audio,
                                               label=label)]
