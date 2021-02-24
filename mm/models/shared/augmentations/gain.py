import numpy as np

from models.shared.augmentations.core import Augmentation


class Gain(Augmentation):

    def __init__(self, min_gain: float, max_gain: float):
        self.normalization = 2 ** 15

        self.min_gain = min_gain
        self.max_gain = max_gain

    def apply(self, audio: np.ndarray, sample_rate: int):
        return np.clip(audio * np.random.uniform(self.min_gain, self.max_gain),
                       -self.normalization,
                       self.normalization).astype(np.int16)
