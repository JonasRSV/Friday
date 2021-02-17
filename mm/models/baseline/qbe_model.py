import os
import sys

# Some systems don't use the launching directory as root
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import numpy as np
import random

from pipelines.evaluate.query_by_example.model import Model, Setting
from pipelines.evaluate.query_by_example.metrics.google_speech_commands.accuracy import per_class_accuracy
from pipelines.evaluate.query_by_example.personal_pipeline import run as personal_run
from pipelines.evaluate.query_by_example.google_speech_commands_pipeline import run as google_run


class Random(Model):
    def register_setting(self, setting: Setting):
        pass

    def __init__(self):
        self.targets = [None]

    def register_keyword(self, keyword: str, utterances: np.ndarray):
        self.targets.append(keyword)

    def infer(self, utterance: np.ndarray):
        return random.choice(self.targets)

    def name(self):
        return "Random"


def run_google_speech_commands_pipeline():
    confusion_block, keywords, all_keywords = google_run(Random(), keywords=["sheila", "wow", "seven"])

    per_class_accuracy(confusion_block, keywords)


def run_personal_pipeline():
    personal_run(Random())


if __name__ == "__main__":
    run_google_speech_commands_pipeline()
    # run_personal_pipeline()
