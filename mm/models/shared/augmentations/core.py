from abc import ABC, abstractmethod
import numpy as np


class Augmentation(ABC):

    @abstractmethod
    def apply(self, audio: np.ndarray, sample_rate: int):
        raise NotImplementedError(f"{__class__} has not implemented apply")
