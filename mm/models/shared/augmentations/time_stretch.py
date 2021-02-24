import numpy as np
import librosa

from models.shared.augmentations.core import Augmentation


class TimeStretch(Augmentation):

    def __init__(self, min_rate: float, max_rate: float):
        self.normalization = 2 ** 15
        self.min_rate = min_rate
        self.max_rate = max_rate

    def apply(self, audio: np.ndarray, sample_rate: int):
        stretched = librosa.effects.time_stretch(audio / self.normalization,
                                                 rate=np.random.uniform(self.min_rate, self.max_rate)
                                                 ) * self.normalization
        stretched = np.array(stretched, dtype=np.int16)

        if len(stretched) > len(audio):
            return stretched[:len(audio)]

        padded_audio = np.zeros_like(audio)
        padded_audio[:len(stretched)] = stretched

        return padded_audio
