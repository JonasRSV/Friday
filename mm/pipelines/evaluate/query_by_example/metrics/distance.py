import pandas as pd
import numpy as np
import time
from tqdm import tqdm


def metrics(df: pd.DataFrame, keywords: [str]):
    caught = 0
    for _, row in df.iterrows():
        caught += ((row[row["utterance"]] > 0) & (row["utterance"] != "None"))

    print("caught", caught)


def realistic_metrics(df: pd.DataFrame, distance: float):
    """Calculate metrics relevant in a realistic scenario.

    E.g first keyword keyword prediction for a keyword
    """

    continue_while_utterance, has_been_correct = "", False
    false_positives, total_none = 0, 0
    correct_later, correct, total = 0, 0, 0
    for _, row in df.iterrows():
        # Ignore all occurrences after first prediction of a keyword
        # Only first prediction is used in the real setting
        is_correct = (row["closest_keyword"] == row["utterance"]) \
                     & (row["distance"] <= distance)

        if row["utterance"] == continue_while_utterance:
            correct_later += (is_correct and not has_been_correct)
            has_been_correct = has_been_correct or is_correct
            continue

        continue_while_utterance, has_been_correct = "", False

        if row["utterance"] == "None":
            total_none += 1
            if distance > row["distance"]:
                false_positives += 1
        else:
            correct += is_correct
            correct_later += is_correct

            has_been_correct = is_correct
            total += 1

            continue_while_utterance = row["utterance"]

    return correct / total, correct_later / total, false_positives / total_none


def metrics_per_distance(df: pd.DataFrame, n: int):
    """Calculate metrics for different distance barriers.

    Args:
        df: DataFrame, output from one of the pipelines
        n: number of discretization steps over all distances
    Returns:
        DF with metric per distance
    """

    print("df", df)

    min_distance = df["distance"].min()
    max_distance = df["distance"].max()

    distance_step = (max_distance - min_distance) / n

    distances = np.array([min_distance + i * distance_step for i in range(n)])

    caughts, got_wrongs, misseds, avoideds = [], [], [], []
    realistic_accuracies, sometime_accuracies, realistic_false_positive_rate = [], [], []
    for d in tqdm(distances):
        caught = 0
        got_wrong = 0
        missed = 0
        avoided = 0
        for _, row in df.iterrows():
            caught += (row["closest_keyword"] == row["utterance"]) \
                      & (row["distance"] <= d)
            got_wrong += (row["closest_keyword"] != row["utterance"]) \
                         & (row["distance"] <= d)
            missed += (row["closest_keyword"] == row["utterance"]) \
                      & (row["distance"] > d)
            avoided += (row["closest_keyword"] != row["utterance"]) \
                       & (row["distance"] > d)

        caughts.append(caught)
        got_wrongs.append(got_wrong)
        misseds.append(missed)
        avoideds.append(avoided)

        accuracy, sometime_accuracy, false_positive_rate = realistic_metrics(df, d)

        realistic_accuracies.append(accuracy)
        sometime_accuracies.append(sometime_accuracy)
        realistic_false_positive_rate.append(false_positive_rate)

    n_df = pd.DataFrame({
        "caught": caughts,
        "got_wrong": got_wrongs,
        "missed": misseds,
        "avoided": avoideds,
        "distance": distances,
        "realistic_accuracy": realistic_accuracies,
        "sometime_accuracy": sometime_accuracies,
        "false_positive_rate": realistic_false_positive_rate,
        "norm_distance": (distances - min_distance) / (max_distance - min_distance)
    })

    n_df["dataset"] = list(df["dataset"])[0]
    n_df["model"] = list(df["model"])[0]
    n_df["time"] = time.time()

    return n_df
