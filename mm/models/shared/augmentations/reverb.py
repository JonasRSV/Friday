import numpy as np
import pysndfx

from models.shared.augmentations.core import Augmentation

class Reverb(Augmentation):

    def __init__(self):
        self.normalization = 2 ** 15

    def apply(self, audio: np.ndarray, sample_rate: int):
        self.effect = (pysndfx.AudioEffectsChain().reverb(
            reverberance=int(np.random.uniform(50, 99)),
            hf_damping=50,
            room_scale=np.random.uniform(30, 100),
            stereo_depth=100,
            pre_delay=20,
            wet_gain=0

        ))
        audio = np.array(audio) / self.normalization
        audio = self.effect(audio, sample_in=sample_rate)
        audio = (audio * self.normalization).astype(np.int16)

        return audio

