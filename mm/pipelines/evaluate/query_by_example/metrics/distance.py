import pandas as pd
import numpy as np
import time
from tqdm import tqdm


def metrics(df: pd.DataFrame, keywords: [str]):
    caught = 0
    for _, row in df.iterrows():
        caught += ((row[row["utterance"]] > 0) & (row["utterance"] != "None"))

    print("caught", caught)


def metrics_per_distance(df: pd.DataFrame, n: int):
    """Calculate metrics for different distance barriers.

    Args:
        df: DataFrame, output from one of the pipelines
        n: number of discretization steps over all distances
    Returns:
        DF with metric per distance
    """

    min_distance = df["distance"].min()
    max_distance = df["distance"].max()

    distance_step = (max_distance - min_distance) / n

    distances = np.array([min_distance + i * distance_step for i in range(n)])

    caughts, got_wrongs, misseds, avoideds = [], [], [], []
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

    n_df = pd.DataFrame({
        "caught": caughts,
        "got_wrong": got_wrongs,
        "missed": misseds,
        "avoided": avoideds,
        "distance": distances,
        "norm_distance": (distances - min_distance) / (max_distance - min_distance)
    })

    n_df["dataset"] = df["dataset"][0]
    n_df["model"] = df["model"][0]
    n_df["time"] = time.time()

    return n_df
