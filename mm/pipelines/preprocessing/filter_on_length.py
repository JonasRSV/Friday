from typing import List
import numpy as np


def acceptable_length(max_length: float, min_length: float, audio: np.ndarray, sample_rate: int) -> bool:
    if min_length <= (len(audio) / sample_rate) <= max_length:
        return True

    return False