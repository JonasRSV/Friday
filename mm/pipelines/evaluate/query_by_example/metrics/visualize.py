import sys
import os

# Some systems dont use the launching directory as root
sys.path.append(os.getcwd())

import pandas as pd
import pipelines.evaluate.query_by_example.core as core
import seaborn as sb
import matplotlib.pyplot as plt
from enum import Enum
import argparse
import pathlib


class Visualizations(Enum):
    PER_DISTANCE_ACCURACY = "per_distance_accuracy"


def per_distance_accuracy(df: pd.DataFrame, dataset: str):
    plt.figure(figsize=(10, 6))
    sb.set_style("whitegrid")
    for model, df in df.groupby(by="model"):
        if len(df.loc[df["norm_distance"] == 0]) > 1:
            print(f"Got multiple copies of the same model for dataset {dataset}")
            print(f"This is incompatible with the 'per_distance_accuracy'... skipping.")
            continue

        accuracy = (df["caught"] + df["avoided"]) / (df["caught"] + df["avoided"] + df["missed"] + df["got_wrong"])

        sb.lineplot(df["norm_distance"], accuracy, label=model)

    plt.ylabel("accuracy", fontsize=16)
    plt.xlabel("distance", fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=16)
    plt.show()


def load(name: str) -> pd.DataFrame:
    friday_data = os.getenv("FRIDAY_DATA")

    if friday_data:
        path = pathlib.Path(friday_data) / name

        if path.is_file():
            return pd.read_csv(path)
        else:
            print(f"{path} is not a valid file")
    else:
        print("Please set environment variable 'FRIDAY_DATA'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, type=str, choices=[v.value for v in core.Pipelines])
    parser.add_argument("--visualization", required=True, type=str, choices=[v.value for v in Visualizations])

    args = parser.parse_args()

    {
        "per_distance_accuracy": lambda x: per_distance_accuracy(load("mpd.csv"), x)

    }[args.visualization](args.dataset)
