"""A DTW model for QbE KWS.

Implementation is based on https://cs.fit.edu/~pkc/papers/tdm04.pdf (this is what the fastdtw package implements)
"""
import os
import sys
# Some systems don't use the launching directory as root
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import numpy as np
from fastdtw import fastdtw
from pipelines.evaluate.query_by_example.model import Model, Setting


def euclidean(x, y):
    return np.sqrt(np.square(x - y).sum())


class FastDTW(Model):
    def register_setting(self, setting: Setting):
        pass

    def __init__(self, max_distance: float):
        self.max_distance = max_distance
        self.keywords_clips = {}
        self.keyword_score = {}

    def register_keyword(self, keyword: str, utterances: np.ndarray):
        self.keywords_clips[keyword] = utterances
        self.keyword_score[keyword] = 0

    def infer(self, utterance: np.ndarray):
        for k in self.keyword_score.keys():
            self.keyword_score[k] = 0

        for keyword, clips in self.keywords_clips.items():
            for clip in clips:
                distance, _ = fastdtw(utterance, clip, dist=euclidean)

                self.keyword_score[keyword] += (distance / len(self.keywords_clips[keyword]))

        scores = sorted(list(self.keyword_score.items()), key=lambda x: x[1])
        best = scores[0]

        if best[1] < self.max_distance:
            return best[0]

        return None

    def name(self):
        return "DTW"


if __name__ == "__main__":
    keyword_clips = {
        "hello": np.random.normal(0, 1, size=(3, 100)),
        "hi": np.random.normal(10, 1, size=(3, 100)),
        "what": np.random.normal(-10, 1, size=(3, 100)),
    }

    utterance = np.random.normal(0.5, 1, size=100)

    dtw = FastDTW(100)
    dtw.register_setting(Setting(
        sample_rate=8000,
        sequence_length=0
    ))
    for keyword, utterances in keyword_clips.items():
        dtw.register_keyword(keyword, utterances)

    print("utterance", dtw.infer(utterance))
