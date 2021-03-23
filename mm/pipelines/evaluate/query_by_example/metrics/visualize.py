import sys
import os
import numpy as np

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
    EFFICACY = "efficacy"
    FALSE_POSITIVE_RATE = "false_positive_rate"
    ACCURACIES = "accuracies"
    CONFUSION = "confusion"


def efficacy(df: pd.DataFrame, dataset: str):
    df = df.loc[df["dataset"] == dataset]
    plt.figure(figsize=(15, 5))
    sb.set_style("whitegrid")

    plots = ["accuracy_as_first", "accuracy_as_some_point", "accuracy_as_majority"]
    for (model, t), df in df.groupby(by=["model", "time"]):
        name = f"{model}-{int(t) % 100}"

        for index, plot_name in enumerate(plots, 1):
            plt.subplot(1, 3, index)
            eff = df[plot_name] / (df["false_positive_rate"] + 0.01)
            sb.lineplot(df["norm_distance"], eff, label=name)

    anchors = [(0.95, 0.9), (0.9, 0.96), (0.92, 0.92)]
    for index, plot_name in enumerate(plots, 1):
        plt.subplot(1, 3, index)

        optimal_eff = 1.0 / (np.zeros_like(df["false_positive_rate"]) + 0.01)

        sb.lineplot(df["norm_distance"], optimal_eff, label="optimal")

        plt.title(plot_name, fontsize=12)
        plt.ylabel("efficacy", fontsize=12)
        plt.xlabel("distance", fontsize=12)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.legend(fontsize=10, bbox_to_anchor=anchors[index - 1])

    plt.savefig(get_plot_dir() / f"efficacy.png", bbox_inches="tight")
    plt.show()


def false_positive_rate(df: pd.DataFrame, dataset: str):
    df = df.loc[df["dataset"] == dataset]
    plt.figure(figsize=(10, 3))
    sb.set_style("whitegrid")
    for (model, t), df in df.groupby(by=["model", "time"]):
        name = f"{model}-{int(t) % 100}"

        sb.lineplot(df["norm_distance"], df["false_positive_rate"], label=name)

    plt.ylabel("false positive rate", fontsize=12)
    plt.xlabel("distance", fontsize=12)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=10)
    plt.savefig(get_plot_dir() / f"false-positives.png", bbox_inches="tight")
    plt.show()


def accuracies(df: pd.DataFrame, dataset: str):
    df = df.loc[df["dataset"] == dataset]
    plt.figure(figsize=(15, 5))
    sb.set_style("whitegrid")
    plots = ["accuracy_as_first", "accuracy_as_some_point", "accuracy_as_majority"]
    for (model, t), df in df.groupby(by=["model", "time"]):
        name = f"{model}-{int(t) % 100}"

        for index, plot_name in enumerate(plots, 1):
            plt.subplot(1, 3, index)
            sb.lineplot(df["norm_distance"], df[plot_name], label=name)

    for index, plot_name in enumerate(plots, 1):
        plt.subplot(1, 3, index)
        plt.ylim([0, 1.1])
        plt.ylabel(plot_name, fontsize=12)
        plt.xlabel("distance", fontsize=12)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.legend(fontsize=10)

    plt.savefig(get_plot_dir() / f"accuracies.png", bbox_inches="tight")
    plt.show()


def confusion_matrix(df: pd.DataFrame, dataset: str):
    df = df.loc[df["dataset"] == dataset]

    keywords = list(df.columns[3: list(df.columns).index("None") + 1])

    groups = list(df.groupby(by=["model", "timestamp"]))
    n_groups = len(groups)
    rows = n_groups // 2

    plt.figure(figsize=(16, rows * 7))
    sb.set_style("whitegrid")
    for i, ((model, t), df) in enumerate(groups[:rows * 2], 1):
        name = f"{model}-{int(t) % 100}"

        confusion_matrix = np.zeros((len(keywords) - 1, len(keywords)))

        for _, row in df.iterrows():
            majority = np.argmax(row[keywords[:-1]])
            if row[keywords][majority] > 0:
                confusion_matrix[keywords.index(row["utterance"])][majority] += 1
            else:
                confusion_matrix[keywords.index(row["utterance"])][-1] += 1
            #for kw in keywords:
            #    confusion_matrix[keywords.index(row["utterance"])][keywords.index(kw)] += row[kw]

        plt.subplot(rows, 2, i)
        plt.title(name, fontsize=12)
        sb.heatmap(confusion_matrix, 
                   cmap=sb.cubehelix_palette(start=2, rot=0, dark=0, light=.6, reverse=True, as_cmap=True),
                   annot=True, square=True, cbar=False, xticklabels=keywords, yticklabels=keywords[:-1])

    for index in range(rows * 2):
        plt.subplot(rows, 2, index + 1)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.yticks(rotation=0)

    plt.savefig(get_plot_dir() / f"confusion-matrix.png", bbox_inches="tight")
    plt.show()


def get_plot_dir():
    friday_data = os.getenv("FRIDAY_DATA")

    if friday_data:
        return pathlib.Path(friday_data) / "plots"
    else:
        print("Please set environment variable 'FRIDAY_DATA'")


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
        "efficacy": lambda x: efficacy(load("metrics_per_distance.csv"), x),
        "false_positive_rate": lambda x: false_positive_rate(load("metrics_per_distance.csv"), x),
        "accuracies": lambda x: accuracies(load("metrics_per_distance.csv"), x),
        "confusion": lambda x: confusion_matrix(load("confusion-matrix.csv"), x)

    }[args.visualization](args.dataset)
