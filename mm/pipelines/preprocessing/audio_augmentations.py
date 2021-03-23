import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
import os
import numpy as np
import models.shared.augmentation as augmentation
import pathlib
import models.shared.augmentations as a
from pipelines.preprocessing.abstract_preprocess_fn import PreprocessFn
from typing import List


class AudioAugmentations(PreprocessFn):

    def __init__(self):
        self.augmenter = augmentation.create_audio_augmentations([
            #a.TimeStretch(min_rate=0.98, max_rate=0.99),
            #a.PitchShift(min_semitones=-1, max_semitones=2),
            #a.Shift(min_rate=-500, max_rate=500),
            a.Gain(min_gain=0.7, max_gain=1.3),
            a.Background(background_noises=pathlib.Path(f"{os.getenv('FRIDAY_DATA', default='data')}/background_noise"),
                         sample_rate=8000,
                         min_voice_factor=0.6,
                         max_voice_factor=0.9),
            a.GaussianNoise(loc=0, stddev=100)
        ],
            p=[
                #0.3,
                #0.3,
                0.25,
                0.95,
                0.3
            ]
        )

    def do(self, example: tf.train.Example) -> List[tf.train.Example]:
        audio = tfexample_utils.get_audio(example)
        audio = np.array(audio, dtype=np.int16)
        sample_rate = tfexample_utils.get_sample_rate(example)
        audio = self.augmenter(audio, sample_rate=sample_rate)
        audio = np.array(audio, dtype=np.int16)
        return [tfexample_utils.set_audio(example=example, audio=audio)]


