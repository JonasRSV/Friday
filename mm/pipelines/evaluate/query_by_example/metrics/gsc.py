import pandas as pd


def multiclass_accuracy(df: pd.DataFrame):
    return (df["utterance"] == df["prediction"]).sum() / len(df)
