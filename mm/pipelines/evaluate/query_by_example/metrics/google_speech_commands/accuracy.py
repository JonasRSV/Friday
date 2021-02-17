import numpy as np


def per_class_accuracy(confusion_block: np.ndarray, keywords: [str]):
    for i, keyword in enumerate(keywords):
        print(
            f"{keyword}: {confusion_block[i, i]} / {confusion_block[:, i].sum() + confusion_block[i].sum()} = {confusion_block[i, i] / (confusion_block[:, i].sum() + confusion_block[i].sum())}")
