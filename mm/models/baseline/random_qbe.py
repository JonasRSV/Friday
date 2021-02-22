import os
import sys
import argparse

# Some systems don't use the launching directory as root
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import numpy as np
import random

from pipelines.evaluate.query_by_example.metrics import personal
from pipelines.evaluate.query_by_example.metrics.storage import append
from pipelines.evaluate.query_by_example.metrics.distance import metrics_per_distance
from pipelines.evaluate.query_by_example.model import Model, Setting
from pipelines.evaluate.query_by_example.personal_pipeline import run as personal_run
from pipelines.evaluate.query_by_example.google_speech_commands_pipeline import run as google_run
from pipelines.evaluate.query_by_example.core import Pipelines


class Random(Model):
    def register_setting(self, setting: Setting):
        pass

    def __init__(self):
        self.targets = [None]

    def register_keyword(self, keyword: str, utterances: np.ndarray):
        self.targets.append(keyword)

    def infer(self, utterance: np.ndarray):
        return random.choice(self.targets), random.choice(self.targets[1:]), 0

    def name(self):
        return "Random"


def run_google_speech_commands_pipeline():
    a = google_run(Random(), keywords=["sheila", "wow", "seven"])

    df = metrics_per_distance(a, 10)
    append("mpd.csv", df)


def run_personal_pipeline():
    """Runs personal evaluation pipeline.

    the pipeline returns two dataframes.

    First: the 'General' dataframe returned by all pipelines
    Second: the 'Personal' specific dataframe that can be used with 'personal' metrics.
    """
    model = Random()
    (a, b), keywords = personal_run(model)
    print(a, b)

    df = metrics_per_distance(a, 10)

    append("mpd.csv", df)

    df = personal.main(df=b, keywords=keywords)
    df["model"] = model.name()

    append("personal.csv", df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline", type=str, choices=[v.value for v in Pipelines])
    args, _ = parser.parse_known_args()

    if args.pipeline == Pipelines.PERSONAL.value:
        run_personal_pipeline()

    if args.pipeline == Pipelines.GOOGLE_SPEECH_COMMANDS.value:
        run_google_speech_commands_pipeline()
