import pandas as pd


def perfect_accuracy(df: pd.DataFrame, keywords: [str]):
    """How many of the keywords got predicted perfectly.

    A perfect prediction occurs when all the predictions within a keywords window is correct or None.
    """

    total, perfect = len(df), 0
    for _, row in df.iterrows():
        for kw in keywords:
            if row[kw] > 0 and kw != row["utterance"]:
                break
        else:
            if row[row["utterance"]] > 0:
                perfect += 1

    return perfect / total


def accuracy(df: pd.DataFrame):
    """How many of the keywords got predicted perfectly.

    A perfect prediction occurs when all the predictions within a keywords window is correct or None.
    """

    total, correct = len(df), 0
    for _, row in df.iterrows():
        if row[row["utterance"]] > 0:
            correct += 1

    return correct / total


def main(df: pd.DataFrame, keywords: [str]):
    return pd.DataFrame({
        "accuracy": [accuracy(df)],
        "perfect_accuracy": [perfect_accuracy(df, keywords=keywords)]
    })
