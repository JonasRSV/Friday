import os
import sys
# Some systems don't use the launching directory as root
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import numpy as np
import random

from pipelines.evaluate.query_by_example.model import Model
from pipelines.evaluate.query_by_example.pipeline import run


class Random(Model):
    def __init__(self):
        self.targets = [None]

    def register_keyword(self, keyword: str, utterances: np.ndarray):
        self.targets.append(keyword)

    def infer(self, utterance: np.ndarray):
        return random.choice(self.targets)

    def name(self):
        return "Random"


if __name__ == "__main__":
    run(Random())
