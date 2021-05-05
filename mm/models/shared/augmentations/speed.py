import numpy as np
import pysndfx

from models.shared.augmentations.core import Augmentation

class Speed(Augmentation):

    def __init__(self):
        self.normalization = 2 ** 15

    def apply(self, audio: np.ndarray, sample_rate: int):
        self.effect = (pysndfx.AudioEffectsChain().speed(
            factor=np.random.uniform(0.8, 1.15)
        ))
        audio = np.array(audio) / self.normalization
        audio = self.effect(audio, sample_in=sample_rate)
        audio = (audio * self.normalization).astype(np.int16)

        return audio

