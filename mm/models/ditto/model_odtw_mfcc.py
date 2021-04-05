"""A DTW model for QbE KWS."""
import os
import sys
import numba

# Some systems don't use the launching directory as root
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import numpy as np
import librosa
from models.ditto.algorithms.odtw import ODTW
from pipelines.evaluate.query_by_example.model import Model, Setting


@numba.jit(nopython=True, fastmath=True)
def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


@numba.jit(nopython=True, fastmath=True)
def distance_fn(x, y):
    # return np.sum(np.square(x - y) / (2 * (x + y)))
    # return np.abs(x - y).sum()
    # return np.sqrt(np.sqrt(np.square(np.square(x - y)).sum()))
    # return -(np.log(softmax(x)) * softmax(y)).sum()
    #x_norm = x / np.sqrt(x @ x)
    #y_norm = y / np.sqrt(y @ y)

    #return 1 - x_norm @ y_norm
    #return np.sqrt(np.square(x - y).sum())
    #return np.sqrt(np.sqrt(np.sqrt(np.square(np.square(np.square(x - y)).sum()))))

    return np.abs(x - y).max()


class ODTWMFCC(Model):
    def distance(self, a: np.ndarray, b: np.ndarray, **kwargs):
        a = self.mfcc_feature(a / self.normalizing)
        b = self.mfcc_feature(b / self.normalizing)

        return self.odtw.distance(a, b, distance=distance_fn)

    def register_setting(self, setting: Setting):
        self.sample_rate = setting.sample_rate
        self.odtw = ODTW(sequence_length=len(self.mfcc_feature(np.random.rand(setting.sequence_length))))

    def __init__(self, max_distance: float):
        self.max_distance = max_distance
        self.keywords_clips = {}
        self.keyword_score = {}

        self.sample_rate = None
        self.odtw = None

        self.normalizing = float(2 ** 15)

    def register_keyword(self, keyword: str, utterances: np.ndarray):
        utterances = utterances / self.normalizing
        self.keywords_clips[keyword] = [self.mfcc_feature(utterance) for utterance in utterances]
        self.keyword_score[keyword] = 0

    def mfcc_feature(self, utterance: np.ndarray):
        return librosa.feature.mfcc(utterance, sr=self.sample_rate,
                                    n_mfcc=13,
                                    n_fft=2048,
                                    hop_length=1024,
                                    win_length=2048,
                                    n_mels=128).T

    def _infer_average_score(self, utterance: np.ndarray):
        for k in self.keyword_score.keys():
            self.keyword_score[k] = 0

        utterance = utterance / self.normalizing
        utterance = self.mfcc_feature(utterance)

        for keyword, mfccs in self.keywords_clips.items():
            for mfcc in mfccs:
                distance = self.odtw.distance(utterance, mfcc, distance=distance_fn)
                self.keyword_score[keyword] += (distance / len(self.keywords_clips[keyword]))

        scores = sorted(list(self.keyword_score.items()), key=lambda x: x[1])
        best = scores[0]

        if best[1] < self.max_distance:
            return best[0], best[0], best[1]

        return None, best[0], best[1]

    def _infer_min_example(self, utterance: np.ndarray):
        utterance = utterance / self.normalizing
        utterance = self.mfcc_feature(utterance)

        min_distance, keyword = 1e9, None
        for kw, mfccs in self.keywords_clips.items():
            for mfcc in mfccs:
                distance = self.odtw.distance(utterance, mfcc, distance=distance_fn)
                # print(kw, distance)
                if distance < min_distance:
                    min_distance = distance
                    keyword = kw

        if min_distance < self.max_distance:
            return keyword, keyword, min_distance

        return None, keyword, min_distance

    def infer(self, utterance: np.ndarray):
        #return self._infer_average_score(utterance)
        return self._infer_min_example(utterance)

    def name(self):
        return "Ghost-DTW-MFCC-CHE"


if __name__ == "__main__":
    keyword_clips = {
        "hello": np.random.normal(0, 1, size=(3, 16000)),
        "hi": np.random.normal(10, 1, size=(3, 16000)),
        "what": np.random.normal(-10, 1, size=(3, 16000)),
    }

    utterance = np.random.normal(0.0, 1, size=16000)

    d = ODTWMFCC(1000)
    d.register_setting(Setting(
        sample_rate=8000,
        sequence_length=16000
    ))
    for keyword, utterances in keyword_clips.items():
        d.register_keyword(keyword, utterances)

    print("utterance", d.infer(utterance))
