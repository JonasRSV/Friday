import os
import sys
import argparse
import time

# Some systems don't use the launching directory as root
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from models.jigglypuff.distances.beam_odtw import BeamODTW
from models.jigglypuff.distances.example_likelihood import ExampleLikelihood
from models.jigglypuff.distances.sample_likelihood import SampleLikelihood
from models.jigglypuff.distances.posteriograms_odtw import PosteriogramsODTW
from enum import Enum

from pipelines.evaluate.query_by_example.metrics import personal
from pipelines.evaluate.query_by_example.metrics.storage import append
from pipelines.evaluate.query_by_example.metrics import distance
from pipelines.evaluate.query_by_example.core import Pipelines
from pipelines.evaluate.query_by_example.personal_pipeline import run as personal_run
from pipelines.evaluate.query_by_example.google_speech_commands_pipeline import run as google_run


class Jigglypuff(Enum):
    BEAMODTW = "BEAMODTW"
    ExampleLikelihood = "ExampleLikelihood"
    SampleLikelihood = "SampleLikelihood"
    PosteriogramsODTW = "PosteriogramsODTW"


def run_google_speech_commands_pipeline(model):
    keywords = ["sheila", "wow", "visual"]

    a = google_run(model, keywords=keywords)

    #df = distance.metrics_per_distance(a, 100)
    #append("mpd.csv", df)
    #distance.metrics(a, keywords=keywords)


def run_personal_pipeline(model):
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

    print(df)


# log(exp(- log(x)) / y) = -log(x) - log y

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline", type=str, choices=[v.value for v in Pipelines])
    parser.add_argument("--jigglypuff", type=str, choices=[v.value for v in Jigglypuff])
    parser.add_argument("--export_dir", type=str, required=True)
    args, _ = parser.parse_known_args()

    model = {
        Jigglypuff.BEAMODTW.value: BeamODTW(export_dir=args.export_dir, max_distance=0.0),
        Jigglypuff.ExampleLikelihood.value: ExampleLikelihood(export_dir=args.export_dir, max_distance=-1),
        Jigglypuff.SampleLikelihood.value: SampleLikelihood(export_dir=args.export_dir, max_distance=-2.85),
        Jigglypuff.PosteriogramsODTW.value: PosteriogramsODTW(export_dir=args.export_dir, max_distance=0.09),
    }

    {
        Pipelines.PERSONAL.value: run_personal_pipeline,
        Pipelines.GOOGLE_SPEECH_COMMANDS.value: run_google_speech_commands_pipeline,
    }[args.pipeline](model[args.jigglypuff])

