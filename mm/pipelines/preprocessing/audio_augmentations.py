import os
import numpy as np
import models.shared.augmentation as augmentation
import pathlib
import models.shared.augmentations as a
from typing import List


class AudioAugmentations:

    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.augmenter = augmentation.create_audio_augmentations([
            #a.TimeStretch(min_rate=0.98, max_rate=0.99),
            #a.PitchShift(min_semitones=-1, max_semitones=2),
            #a.Shift(min_rate=-500, max_rate=500),
            #a.Gain(min_gain=0.8, max_gain=1.3),
            #a.Speed()
            a.Reverb(),
            a.Background(background_noises=pathlib.Path(f"{os.getenv('FRIDAY_DATA', default='data')}/background_noise"),
                         sample_rate=sample_rate,
                         min_voice_factor=0.7,
                         max_voice_factor=0.95),
            a.GaussianNoise(loc=0, stddev=100)
        ],
            p=[
                #0.3,
                #0.3,
                #0.25,
                0.8,
                0.8,
                0.3
            ]
        )

    def do(self, audio: np.array) -> np.ndarray:
        audio = self.augmenter(audio, sample_rate=self.sample_rate)
        audio = np.array(audio, dtype=np.int16)
        return audio


