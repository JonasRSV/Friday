import pandas as pd


def multiclass_accuracy(df: pd.DataFrame):
    return (df["utterance"] == df["closest_keyword"]).sum() / len(df)
