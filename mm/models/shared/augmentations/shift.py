import numpy as np

from models.shared.augmentations.core import Augmentation


class Shift(Augmentation):

    def __init__(self, min_rate: float, max_rate: float):
        self.normalization = 2 ** 15
        self.min_rate = min_rate
        self.max_rate = max_rate

    def apply(self, audio: np.ndarray, sample_rate: int):
        return np.roll(audio, int(np.random.uniform(self.min_rate, self.max_rate)))


