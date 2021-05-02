from typing import List
import tensorflow as tf
import numpy as np
import models.shared.augmentations as a
import random

def create_audio_augmentations(aug: List[a.Augmentation], p: np.ndarray):
    if len(aug) != len(p):
        raise ValueError(f"Length of augmentations must match distribution {len(aug)} != {len(p)}")

    def audio_augmentations(audio: np.ndarray, sample_rate: int):
        for aug_to_apply, with_prob in zip(aug, p):
            if np.random.rand() < with_prob:
                audio = aug_to_apply.apply(audio, sample_rate)

        return audio

    return audio_augmentations
