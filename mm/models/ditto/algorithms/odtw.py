import numpy as np
import time
import numba
from typing import Callable


@numba.jit(nopython=True, fastmath=True)
def dtw(x, template, mem, template_length, sequence_length, distance):
    for j in range(1, template_length - 1):
        mem[0, j] = mem[0, j - 1] + distance(x[0], template[j - 1])

    mem[0, template_length - 1] = mem[0, template_length - 2]

    for i in range(1, sequence_length):
        for j in range(1, template_length - 1):
            mem[i, j] = min(mem[i - 1, j], mem[i, j - 1], mem[i - 1, j - 1]) + distance(x[i], template[j - 1])

    for i in range(1, sequence_length):
        mem[i, template_length - 1] = min(mem[i, template_length - 2], mem[i - 1, template_length - 1],
                                          mem[i - 1, template_length - 2])

    return mem[sequence_length - 1, template_length - 1]


class ODTW:
    """Open Dynamic Time Warping.

    A dynamic time warping algorithm that finds the best subsequence match of a template to a sequence.
    """

    def __init__(self, sequence_length: int):
        # Plus two for 'empty' token in start and end
        # The template does not actually contain these though
        # So we have to add offsets when calculating its indices
        self.template_length = sequence_length + 2

        self.sequence_length = sequence_length
        self.mem = np.zeros((self.sequence_length, self.template_length))

    def distance(self, x: np.ndarray, template: np.ndarray, distance: Callable[[np.ndarray, np.ndarray], float]):
        if len(x) != len(template):
            raise Exception(f"Sequences should be padded to same length {len(x)} != {len(template)}")
        mem = self.mem
        template_length = self.template_length
        sequence_length = self.sequence_length

        return dtw(x, template, mem, template_length, sequence_length, distance)


if __name__ == "__main__":
    # sequence = [0, 1, 2, 1, 0, 0, 0]
    # template = [1, 1, 1, 2, 1, 2, 1]

    s1 = np.random.normal(0, 1, size=16000)
    s2 = np.random.normal(4, 1, size=16000)
    s3 = np.random.normal(-4, 1, size=16000)

    template = np.random.normal(0, 1, size=16000)

    odtw = ODTW(len(s1))


    @numba.jit(nopython=True, fastmath=True)
    def eu(x, y):
        return np.sqrt(np.square(x - y))


    timestamp = time.time()
    print(odtw.distance(s1, template, distance=eu))
    print(time.time() - timestamp)
    timestamp = time.time()
    print(odtw.distance(s2, template, distance=eu))
    print(time.time() - timestamp)
    timestamp = time.time()
    print(odtw.distance(s3, template, distance=eu))
    print(time.time() - timestamp)
