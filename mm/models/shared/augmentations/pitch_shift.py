import numpy as np
import librosa

from models.shared.augmentations.core import Augmentation


class PitchShift(Augmentation):

    def __init__(self, min_semitones: int, max_semitones: int):
        self.normalization = 2 ** 15
        self.min_semitones = min_semitones
        self.max_semitones = max_semitones

    def apply(self, audio: np.ndarray, sample_rate: int):
        return librosa.effects.pitch_shift(audio / self.normalization,
                                           sr=sample_rate,
                                           n_steps=np.random.uniform(self.min_semitones, self.max_semitones)
                                           ) * self.normalization
