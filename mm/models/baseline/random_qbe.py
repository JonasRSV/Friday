import os
import sys
import argparse
import time

# Some systems don't use the launching directory as root
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import numpy as np
import random

from pipelines.evaluate.query_by_example.metrics import distance
from pipelines.evaluate.query_by_example.metrics import personal
from pipelines.evaluate.query_by_example.metrics.storage import append
from pipelines.evaluate.query_by_example.metrics.distance import metrics_per_distance
from pipelines.evaluate.query_by_example.model import Model, Setting
from pipelines.evaluate.query_by_example.usability_pipeline import run as usability_run
from pipelines.evaluate.query_by_example.personal_pipeline import run as personal_run
from pipelines.evaluate.query_by_example.resources_pipeline import run as resource_run
from pipelines.evaluate.query_by_example.google_speech_commands_pipeline import run as google_run
from pipelines.evaluate.query_by_example.core import Pipelines


class Random(Model):
    def distance(self, a: np.ndarray, b: np.ndarray, **kwargs):
        return np.random.rand()

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
    df = google_run(Random(), keywords=["left", "learn", "sheila", "seven", "dog", "down"])

    append("google_speech_commands_results.csv", df)


def run_personal_pipeline():
    """Runs personal evaluation pipeline."""
    model = Random()

    (a, b), keywords = personal_run(model)

    df = distance.metrics_per_distance(a, 100, len(b), keywords)
    append("metrics_per_distance.csv", df)
    # distance.metrics(a, keywords=keywords)

    print("max efficacy", df["efficacy"].max())
    distance_maximizing_efficacy = df.iloc[df["efficacy"].argmax()]["distance"]
    print("best distance", distance_maximizing_efficacy)
    print(a)

    b = distance.b_from_a(a, keywords, distance_maximizing_efficacy)
    b["timestamp"] = time.time()
    # print("b\n", b)
    # print("b from a\n", distance.b_from_a(a, keywords, distance_maximizing_efficacy))

    append("confusion-matrix.csv", b)
    # df = personal.main(df=b, keywords=keywords)
    # df["model"] = model.name()
    # append("personal.csv", df)


def run_resource_pipeline():
    """Runs resource evaluation pipeline."""
    model_fn = lambda: Random()
    df = resource_run(model_fn, K=100, N=100)

    print(df)


def run_usability_pipeline():
    """Runs resource evaluation pipeline."""
    model_fn = lambda: Random()
    df = usability_run(model_fn)

    print(df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline", type=str, choices=[v.value for v in Pipelines])
    args, _ = parser.parse_known_args()

    if args.pipeline == Pipelines.PERSONAL.value:
        run_personal_pipeline()

    if args.pipeline == Pipelines.GOOGLE_SPEECH_COMMANDS.value:
        run_google_speech_commands_pipeline()

    if args.pipeline == Pipelines.RESOURCE.value:
        run_resource_pipeline()

    if args.pipeline == Pipelines.USABILITY.value:
        run_usability_pipeline()
