import os
import sys
import argparse
import time

# Some systems don't use the launching directory as root
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from models.bulbasaur.inference.simple import Simple
from enum import Enum

from pipelines.evaluate.query_by_example.usability_pipeline import run as usability_run
from pipelines.evaluate.query_by_example.resources_pipeline import run as resource_run
from pipelines.evaluate.query_by_example.metrics import personal
from pipelines.evaluate.query_by_example.metrics.storage import append
from pipelines.evaluate.query_by_example.metrics import distance
from pipelines.evaluate.query_by_example.core import Pipelines
from pipelines.evaluate.query_by_example.personal_pipeline import run as personal_run
from pipelines.evaluate.query_by_example.google_speech_commands_pipeline import run as google_run


class Bulbasaur(Enum):
    Simple = "Simple"


def run_google_speech_commands_pipeline(model_fn):
    keywords = ["dog", "down", "learn", "left", "seven", "sheila"]

    df = google_run(model_fn(), keywords=keywords)

    append("google_speech_commands_results.csv", df)


def run_personal_pipeline(model_fn):
    (a, b), keywords = personal_run(model_fn())

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

    print(df)

def run_resource_pipeline(model_fn):
    """Runs resource evaluation pipeline."""
    df = resource_run(model_fn, K=30, N=100)
    append("latency.csv", df)

def run_usability_pipeline(model_fn):
    """Runs resource evaluation pipeline."""
    df = usability_run(model_fn)

    append("usability.csv", df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline", type=str, choices=[v.value for v in Pipelines])
    parser.add_argument("--bulbasaur", type=str, choices=[v.value for v in Bulbasaur])
    parser.add_argument("--export_dir", type=str, required=True)
    args, _ = parser.parse_known_args()

    model = {
        Bulbasaur.Simple.value: lambda: Simple(export_dir=args.export_dir, max_distance=1),
    }

    {
        Pipelines.PERSONAL.value: run_personal_pipeline,
        Pipelines.GOOGLE_SPEECH_COMMANDS.value: run_google_speech_commands_pipeline,
        Pipelines.USABILITY.value: run_usability_pipeline,
        Pipelines.RESOURCE.value: run_resource_pipeline,
    }[args.pipeline](model[args.bulbasaur])
