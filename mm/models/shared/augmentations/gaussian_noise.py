import numpy as np

from models.shared.augmentations.core import Augmentation


class GaussianNoise(Augmentation):

    def __init__(self, loc: int, stddev: int):
        """Apply gaussian noise.

        The parameters are given in the range -2**15 -> 2**15 since the audio will be 16bit ints.
        """
        self.normalization = 2 ** 15

        self.loc = loc / self.normalization
        self.stddev = stddev / self.normalization

    def apply(self, audio: np.ndarray, sample_rate: int):
        audio = np.array(audio)
        return audio + np.clip(
            np.random.normal(loc=self.loc, scale=self.stddev, size=audio.shape) * self.normalization,
            -self.normalization,
            self.normalization)
