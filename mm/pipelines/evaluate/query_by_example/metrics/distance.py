import sys
import pandas as pd
import numpy as np
import time
from tqdm import tqdm

epsilon = 1e-15


def metrics(df: pd.DataFrame, keywords: [str]):
    caught = 0
    for _, row in df.iterrows():
        caught += ((row[row["utterance"]] > 0) & (row["utterance"] != "None"))

    print("caught", caught)


def b_from_a(df: pd.DataFrame, keywords: [str], distance: float):
    """..."""

    def get_new_row(id: int, utterance: int, sample: int, model: str, dataset: str):
        return ([id, utterance, sample] + [0] * (len(keywords) + 1)) + [model, dataset]

    active_keyword, active_row, rows = None, None, []

    for _, row in df.iterrows():

        if row["utterance"] in keywords:
            if not active_row:
                active_row = get_new_row(row["id"], row["utterance"], row["sample"], row["model"], row["dataset"])

            if row["distance"] <= distance:
                active_row[3 + keywords.index(row["closest_keyword"])] += 1
            else:
                active_row[3 + len(keywords)] += 1

        elif active_row:
            rows.append(active_row)
            active_row = None

    if active_row:
        rows.append(active_row)

    return pd.DataFrame(rows, columns=["id", "utterance", "sample"] + keywords + ["None", "model", "dataset"])


def realistic_metrics(df: pd.DataFrame, distance: float, total: int, keywords: [str]):
    """Calculate metrics relevant in a realistic scenario.

    To whomever reads this function.. I'm sorry.


    E.g first keyword keyword prediction for a keyword
    """

    active_keywords = {kw: 0 for kw in keywords}
    predicted_keywords = {kw: False for kw in keywords}
    been_correct_at_some_point = {kw: False for kw in keywords}
    majority_vote = {kw: [0] * len(keywords) for kw in keywords}

    false_positives, total_none, correct_at_some_point, correct_as_majority, correct_at_first = 0, 0, 0, 0, 0

    current_task = 0
    for _, row in df.iterrows():

        # Reset cause we're entering a new task
        if row["task"] != current_task:
            current_task = row["task"]

            for key in active_keywords.keys():
                if active_keywords[key]:
                    correct_as_majority += keywords[np.argmax(majority_vote[key])] == key
                    correct_at_some_point += been_correct_at_some_point[key]

            active_keywords = {kw: 0 for kw in keywords}
            predicted_keywords = {kw: False for kw in keywords}
            been_correct_at_some_point = {kw: False for kw in keywords}
            majority_vote = {kw: [0] * len(keywords) for kw in keywords}

        # Ignore all occurrences after first prediction of a keyword
        # Only first prediction is used in the real setting
        is_correct = (row[row["closest_keyword"]] > 0)
        is_prediction = (row["distance"] <= distance)

        if row["utterance"] == "None":
            total_none += 1
            if is_prediction:
                false_positives += 1

            continue

        if not predicted_keywords[row["closest_keyword"]] \
                and is_correct and is_prediction:
            correct_at_first += 1

        for key in active_keywords.keys():

            if active_keywords[key] and row[key] == 0:
                correct_as_majority += (keywords[np.argmax(majority_vote[key])] == key) \
                                       and (np.max(majority_vote[key]) > 0)
                correct_at_some_point += been_correct_at_some_point[key]

                # Reset
                majority_vote[key] = [0] * len(keywords)
                been_correct_at_some_point[key] = False
                predicted_keywords[key] = False

            active_keywords[key] = row[key] > 0

            if is_prediction and active_keywords[key]:
                predicted_keywords[key] = True

        if is_prediction:
            for key, active in active_keywords.items():
                if active:
                    majority_vote[key][keywords.index(row["closest_keyword"])] += 1

            if is_correct:
                been_correct_at_some_point[row["closest_keyword"]] = True

    for key in active_keywords.keys():
        if active_keywords[key]:
            correct_as_majority += keywords[np.argmax(majority_vote[key])] == key
            correct_at_some_point += been_correct_at_some_point[key]

    # print("correct", correct_at_first, "total", total, "correct_at_some_point",
    #      correct_at_some_point, "majority_vote", correct_as_majority, "fp", false_positives, "total_none",
    #      total_none)

    return correct_at_first / total, correct_at_some_point / total, correct_as_majority / total, false_positives / (
            total_none + epsilon)


def metrics_per_distance(df: pd.DataFrame, n: int, total: int, keywords: [str]):
    """Calculate metrics for different distance barriers.

    Args:
        df: DataFrame, output from one of the pipelines
        n: number of discretization steps over all distances
        total: total number of keyword utterances in the df
        keywords: The keywords known by the system
    Returns:
        DF with metric per distance
    """

    print("df", df.head(60))
    print("df", df.tail(60))

    min_distance = df["distance"].min()
    max_distance = df["distance"].max()

    distance_step = (max_distance - min_distance) / n

    distances = np.array([min_distance + i * distance_step for i in range(n)] + [max_distance + 0.000001])

    efficacies = []
    caughts, got_wrongs, misseds, avoideds = [], [], [], []
    accuracies_as_first, accuracies_as_some_point, accuracies_as_majority, realistic_false_positive_rate = [], [], [], []
    for d in tqdm(distances):
        caught = 0
        got_wrong = 0
        missed = 0
        avoided = 0
        for _, row in df.iterrows():
            caught += (row[row["closest_keyword"]] > 0) \
                      & (row["distance"] <= d)
            got_wrong += (row[row["closest_keyword"]] == 0) \
                         & (row["distance"] <= d)
            missed += (row[row["closest_keyword"]] > 0) \
                      & (row["distance"] > d)
            avoided += (row[row["closest_keyword"]] == 0) \
                       & (row["distance"] > d)

        caughts.append(caught)
        got_wrongs.append(got_wrong)
        misseds.append(missed)
        avoideds.append(avoided)

        accuracy_as_first, accuracy_as_some_point, accuracy_as_majority, false_positive_rate = \
            realistic_metrics(df, d, total, keywords)

        accuracies_as_first.append(accuracy_as_first)
        accuracies_as_some_point.append(accuracy_as_some_point)
        accuracies_as_majority.append(accuracy_as_majority)
        realistic_false_positive_rate.append(false_positive_rate)

        efficacies.append(accuracy_as_majority / (false_positive_rate + 0.01))

    n_df = pd.DataFrame({
        "efficacy": efficacies,
        "caught": caughts,
        "got_wrong": got_wrongs,
        "missed": misseds,
        "avoided": avoideds,
        "distance": distances,
        "accuracy_as_first": accuracies_as_first,
        "accuracy_as_some_point": accuracies_as_some_point,
        "accuracy_as_majority": accuracies_as_majority,
        "false_positive_rate": realistic_false_positive_rate,
        "norm_distance": (distances - min_distance) / (max_distance - min_distance)
    })

    n_df["dataset"] = list(df["dataset"])[0]
    n_df["model"] = list(df["model"])[0]
    n_df["time"] = time.time()

    return n_df
