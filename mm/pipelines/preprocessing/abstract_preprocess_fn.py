import tensorflow as tf
from abc import ABC, abstractmethod
from typing import List


class PreprocessFn(ABC):

    @abstractmethod
    def do(self, example: tf.train.Example) -> List[tf.train.Example]:
        raise NotImplemented("do is not implemented")
