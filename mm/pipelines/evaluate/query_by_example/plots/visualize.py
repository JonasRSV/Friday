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
from pipelines.evaluate.query_by_example.metrics.gsc import multiclass_accuracy
import argparse
import pathlib


class Visualizations(Enum):
    EFFICACY = "efficacy"
    FALSE_POSITIVE_RATE = "false_positive_rate"
    ACCURACIES = "accuracies"
    CONFUSION = "confusion"
    LATENCY = "latency"
    GCS_ACCURACY = "gcs_accuracy"
    GCS_CONFUSION = "gcs_confusion"
    GCS_DISTRIBUTION = "gcs_distribution"
    USABILITY = "usability"


def efficacy(df: pd.DataFrame):
    plt.figure(figsize=(15, 5))
    sb.set_style("whitegrid")

    plots = ["accuracy_as_first", "accuracy_as_some_point", "accuracy_as_majority"]
    for (model, t), df in df.groupby(by=["model", "time"]):
        name = f"{model}-{int(t) % 100}"

        for index, plot_name in enumerate(plots, 1):
            plt.subplot(1, 3, index)
            eff = df[plot_name] / (df["false_positive_rate"] + 0.01)

            if index == 3:
                sb.lineplot(df["norm_distance"], eff, label=name)
            else:
                sb.lineplot(df["norm_distance"], eff)

    # anchors = [(0.8, 0.9), (0.9, 0.96), (0.92, 0.92)]
    for index, plot_name in enumerate(plots, 1):
        plt.subplot(1, 3, index)

        # optimal_eff = 1.0 / (np.zeros_like(df["false_positive_rate"]) + 0.01)

        # sb.lineplot(df["norm_distance"], optimal_eff, label="optimal")

        plt.title(plot_name, fontsize=12)
        plt.ylabel("efficacy", fontsize=12)
        plt.xlabel("distance", fontsize=12)
        plt.ylim([0, 100])
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)

    plt.legend(fontsize=12, bbox_to_anchor=(-0.3, -0.2))

    plt.savefig(get_plot_dir() / f"efficacy.png", bbox_inches="tight")
    plt.show()


def false_positive_rate(df: pd.DataFrame):
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


def accuracies(df: pd.DataFrame):
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


def confusion_matrix(df: pd.DataFrame):
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
            # for kw in keywords:
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


def latencies(df: pd.DataFrame):
    with sb.plotting_context(rc={"legend.fontsize": 16,
                                 "legend.title_fontsize": 16}):
        plt.figure(figsize=(10, 4))
        sb.set_style("whitegrid")
        sb.lineplot(x="K", y="latency", data=df, hue="model", style="model", markers=True, dashes=True, ci=68)

        plt.plot(np.arange(0, df["K"].max() + 2), np.ones(df["K"].max() + 2) * 0.25, 'r--')

        plt.xlim([0, df["K"].max() + 1])
        plt.yscale("log")
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        plt.ylabel("L(K)", fontsize=20)
        plt.xlabel("K", fontsize=20)

        plt.savefig(get_plot_dir() / f"latencies.png", bbox_inches="tight")
        plt.show()


def gcs_accuracy(df: pd.DataFrame):
    names, accuracies = [], []
    for (model, t), df in df.groupby(by=["model", "time"]):
        names.append(model)
        accuracies.append(multiclass_accuracy(df))

    plt.figure(figsize=(10, 4))
    sb.set_style("whitegrid")
    pal = sb.cubehelix_palette(start=2, rot=0, dark=0.15, light=.7, reverse=False, n_colors=len(names))
    accuracies = np.array(accuracies)

    rank = accuracies.argsort().argsort()  # http://stackoverflow.com/a/6266510/1628638
    sb.barplot(x=names, y=accuracies, palette=np.array(pal[::-1])[rank])

    plt.ylim([0, 1])
    plt.ylabel("accuracy", fontsize=16)
    plt.yticks(fontsize=11)
    plt.xticks(fontsize=14)
    plt.savefig(get_plot_dir() / f"gsc_accuracies.png", bbox_inches="tight")
    plt.show()


def gcs_confusion(df: pd.DataFrame):
    keywords = list(df["utterance"].unique())
    groups = list(df.groupby(by=["model", "time"]))
    n_groups = len(groups)
    rows = n_groups // 2

    plt.figure(figsize=(16, rows * 7))
    sb.set_style("whitegrid")
    for i, ((model, t), df) in enumerate(groups[:rows * 2], 1):
        name = f"{model}-{int(t) % 100}"

        confusion_matrix = np.zeros((len(keywords), len(keywords)))

        for _, row in df.iterrows():
            if str(row["prediction"]) != "nan":
                confusion_matrix[keywords.index(row["utterance"]), keywords.index(row["prediction"])] += 1

        plt.subplot(rows, 2, i)
        plt.title(name, fontsize=12)
        sb.heatmap(confusion_matrix,
                   cmap=sb.cubehelix_palette(start=2, rot=0, dark=0, light=.6, reverse=True, as_cmap=True),
                   annot=True, square=True, cbar=False, xticklabels=keywords, yticklabels=keywords)

    for index in range(rows * 2):
        plt.subplot(rows, 2, index + 1)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.yticks(rotation=0)

    plt.savefig(get_plot_dir() / f"gsc-confusion-matrix.png", bbox_inches="tight")
    plt.show()


def gcs_distribution(df: pd.DataFrame):
    data = []
    for _, df in df.groupby(by=["model", "time"]):
        data = df["utterance"].value_counts()
        break

    print("data", data)
    print("data", type(data))
    plt.figure(figsize=(10, 4))
    sb.set_style("whitegrid")
    pal = sb.cubehelix_palette(start=2, rot=0, dark=0.15, light=.7, reverse=False, n_colors=len(data))

    rank = data.argsort().argsort()  # http://stackoverflow.com/a/6266510/1628638
    sb.barplot(x=data.index, y=data.values, palette=np.array(pal[::-1])[rank])

    plt.ylabel("samples", fontsize=16)
    plt.yticks(fontsize=11)
    plt.xticks(fontsize=14)
    plt.savefig(get_plot_dir() / f"gsc_distribution.png", bbox_inches="tight")
    plt.show()


def usability(df: pd.DataFrame):
    colors = sb.color_palette()
    # colors = sb.color_palette("rocket")
    for j, ((model, _), df) in enumerate(df.groupby(by=["model", "time"])):
        plt.figure(figsize=(10, 2))
        sb.set_style("whitegrid")
        for i, (keyword, from_df) in enumerate(df.groupby(by="from")):
            same = from_df.loc[from_df["to"] == keyword]["distance"]
            different = from_df.loc[from_df["to"] != keyword]["distance"]

            sb.distplot(same, hist=False, label=f"${keyword}$", color=colors[i])
            sb.distplot(different, hist=False, kde_kws={"linestyle": "--"},
                        color=colors[i])

            print("keyword", keyword)

        # sb.kdeplot(data=df, x="distance", hue="from")
        plt.title(model, fontsize=14)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.legend(fontsize=10)
        plt.savefig(get_plot_dir() / f"usability-{j}.png", bbox_inches="tight")
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
    parser.add_argument("--visualization", required=True, type=str, choices=[v.value for v in Visualizations])

    args = parser.parse_args()

    {
        "efficacy": lambda: efficacy(load("metrics_per_distance.csv")),
        "false_positive_rate": lambda: false_positive_rate(load("metrics_per_distance.csv")),
        "accuracies": lambda: accuracies(load("metrics_per_distance.csv")),
        "confusion": lambda: confusion_matrix(load("confusion-matrix.csv")),
        "latency": lambda: latencies(load("latency.csv")),
        "gcs_accuracy": lambda: gcs_accuracy(load("google_speech_commands_results.csv")),
        "gcs_confusion": lambda: gcs_confusion(load("google_speech_commands_results.csv")),
        "gcs_distribution": lambda: gcs_distribution(load("google_speech_commands_results.csv")),
        "usability": lambda: usability(load("usability.csv")),

    }[args.visualization]()
