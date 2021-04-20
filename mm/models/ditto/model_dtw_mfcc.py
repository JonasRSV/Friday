"""A DTW model for QbE KWS."""
import os
import sys

# Some systems don't use the launching directory as root
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import numpy as np
import librosa
from dtw import dtw
from pipelines.evaluate.query_by_example.model import Model, Setting


def euclidean(x, y):
    return np.sqrt(np.square(x - y).sum())


class DTWMFCC(Model):

    def mfcc_feature(self, utterance: np.ndarray):
        #return librosa.feature.mfcc(utterance, sr=self.sample_rate,
        #                            n_mfcc=13,
        #                            n_fft=2048,
        #                            hop_length=1024,
        #                            win_length=2048,
        #                            n_mels=128).T
        return librosa.feature.mfcc(utterance, sr=self.sample_rate,
                                    n_mfcc=20,
                                    n_fft=2048,
                                    hop_length=512,
                                    win_length=2048,
                                    n_mels=128).T

    def distance(self, a: np.ndarray, b: np.ndarray, **kwargs):
        a = self.mfcc_feature(a / 2**15)
        b = self.mfcc_feature(b / 2**15)

        distance, _, _, _ = dtw(a, b, dist=euclidean)

        return distance

    def register_setting(self, setting: Setting):
        self.sample_rate = setting.sample_rate

    def __init__(self, max_distance: float):
        self.max_distance = max_distance
        self.keywords_clips = {}
        self.keyword_score = {}

        self.sample_rate = None

    def register_keyword(self, keyword: str, utterances: np.ndarray):
        utterances = utterances / 2 ** 15

        self.keywords_clips[keyword] = [self.mfcc_feature(utterance) for utterance in utterances]

        self.keyword_score[keyword] = 0

    def _infer_min_example(self, utterance: np.ndarray):
        utterance = utterance / 2**15
        utterance = self.mfcc_feature(utterance)

        min_distance, keyword = 1e9, None
        for kw, mfccs in self.keywords_clips.items():
            for mfcc in mfccs:
                distance, _, _, _ = dtw(utterance, mfcc, dist=euclidean)
                if distance < min_distance:
                    min_distance = distance
                    keyword = kw

        if min_distance < self.max_distance:
            return keyword, keyword, min_distance

        return None, keyword, min_distance

    def infer(self, utterance: np.ndarray):
        return self._infer_min_example(utterance)

    def name(self):
        return "DTW-MFCC-EU"


if __name__ == "__main__":
    keyword_clips = {
        "hello": np.random.normal(0, 1, size=(3, 16000)),
        "hi": np.random.normal(10, 1, size=(3, 16000)),
        "what": np.random.normal(-10, 1, size=(3, 16000)),
    }

    utterance = np.random.normal(0.0, 1, size=16000)

    d = DTWMFCC(1000)
    d.register_setting(Setting(
        sample_rate=8000,
        sequence_length=0
    ))
    for keyword, utterances in keyword_clips.items():
        d.register_keyword(keyword, utterances)

    print("utterance", d.infer(utterance))
