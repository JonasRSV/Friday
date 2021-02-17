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
    def register_setting(self, setting: Setting):
        self.sample_rate = setting.sample_rate

    def __init__(self, max_distance: float):
        self.max_distance = max_distance
        self.keywords_clips = {}
        self.keyword_score = {}

        self.sample_rate = None

    def register_keyword(self, keyword: str, utterances: np.ndarray):
        utterances = utterances / np.abs(utterances).max(axis=-1)[:, None]

        self.keywords_clips[keyword] = [
            librosa.feature.mfcc(utterance, sr=self.sample_rate,
                                 n_mfcc=40,
                                 n_fft=1024,
                                 hop_length=512,
                                 win_length=1024,
                                 n_mels=80) for utterance in utterances]

        self.keyword_score[keyword] = 0

    def infer(self, utterance: np.ndarray):
        for k in self.keyword_score.keys():
            self.keyword_score[k] = 0

        utterance = utterance / np.abs(utterance).max()
        utterance = librosa.feature.mfcc(utterance, sr=8000,
                                         n_mfcc=40,
                                         n_fft=1024,
                                         hop_length=512,
                                         win_length=1024,
                                         n_mels=80)

        for keyword, mfccs in self.keywords_clips.items():
            for mfcc in mfccs:
                distance, _, _, _ = dtw(utterance, mfcc, dist=euclidean)
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
