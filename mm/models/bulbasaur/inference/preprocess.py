import numpy as np


def fix_loudness(x: np.ndarray):
    return np.array(x, dtype=np.int16)
    #return np.array(x * 15, dtype=np.int16)

