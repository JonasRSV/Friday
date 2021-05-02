import os
import sys
import argparse
import time

# Some systems don't use the launching directory as root
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from models.bulbasaur.inference.simple import Simple
from enum import Enum

class Bulbasaur(Enum):
    Simple = "Simple"


def run_google_speech_commands_pipeline(model_fn):
    # TODO:
    keywords = ["dog", "down", "learn", "left", "seven", "sheila"]


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
