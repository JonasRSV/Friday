import os
import numpy as np
import numba
import random
from models.ditto.algorithms.odtw import dtw
from models.jigglypuff.distances.preprocess import fix_loudness

import models.jigglypuff.distances.base as base
from pipelines.evaluate.query_by_example.model import Setting


@numba.jit(nopython=True, fastmath=True)
def discrete(x, y):
    return 1 - (x == y)


class BeamODTW(base.Base):
    def distance(self, a: np.ndarray, b: np.ndarray, **kwargs):
        a = fix_loudness(a)
        b = fix_loudness(b)

        a, _ = self.get_output(a)
        b, _ = self.get_output(b)

        return self.ghost_dtw(a, b) / len(b)

    def __init__(self, export_dir: str, max_distance: float):
        base.Base.__init__(self, export_dir=export_dir)

        self.max_distance = max_distance
        self.keyword_phoneme_seq = {}

    def register_keyword(self, keyword: str, utterances: np.ndarray):
        utterances = fix_loudness(utterances)

        if keyword not in self.keyword_phoneme_seq:
            self.keyword_phoneme_seq[keyword] = []

        for utterance in utterances:
            seq, _ = self.get_output(utterance)

            self.keyword_phoneme_seq[keyword].append(seq)

        self.keywords = list(self.keyword_phoneme_seq.keys())
        print(self.keyword_phoneme_seq)

    def ghost_dtw(self, a: np.ndarray, b: np.ndarray):
        x = a
        template = b
        sequence_length = len(x)
        template_length = len(template) + 2
        mem = np.zeros((sequence_length, template_length))

        return dtw(x=x,
                   template=template,
                   mem=mem,
                   sequence_length=sequence_length,
                   template_length=template_length,
                   distance=discrete)

    def infer_min_avg_distance(self, utterance: np.ndarray):
        min_distance, keyword = 1e9, None
        ut_seq, _ = self.get_output(utterance)

        for kw, seqs in self.keyword_phoneme_seq.items():
            score = 0
            for seq in seqs:
                score += self.ghost_dtw(ut_seq, seq)

            if score < min_distance:
                min_distance = score
                keyword = kw

        if min_distance < self.max_distance:
            return keyword, keyword, min_distance

        return None, keyword, min_distance

    def infer_min_distance(self, utterance: np.ndarray):
        min_distance, keyword = 1e9, None
        ut_seq, _ = self.get_output(utterance)

        if len(ut_seq) == 0:
            return None, random.choice(self.keywords), 1.1

        for kw, seqs in self.keyword_phoneme_seq.items():
            for seq in seqs:
                distance = self.ghost_dtw(ut_seq, seq) #/ len(seq)

                if distance < min_distance:
                    min_distance = distance
                    keyword = kw

        if min_distance < self.max_distance:
            return keyword, keyword, min_distance

        return None, keyword, min_distance

    def infer(self, utterance: np.ndarray):
        utterance = fix_loudness(utterance)
        # return self.infer_min_avg_distance(utterance)
        return self.infer_min_distance(utterance)

    def name(self):
        return "STP-BS"

    def register_setting(self, setting: Setting):
        pass


if __name__ == "__main__":
    model = BeamODTW(export_dir=f"{os.getenv('FRIDAY_ROOT')}/mm/data/stp_model/1614070522",
                     max_distance=1000)

    mock_audio = (np.random.rand(16000) * 30000).astype(np.int16)
    mock_labels = np.array([10, 20, 0, 10, 10, 20, 0, 10, 12])
    output, output_shape = model.get_output(mock_audio)

    print("output_shape", output_shape)
    print("output", output)

    logits, logits_shape = model.get_logits(mock_audio)

    print("logits_shape", logits_shape)
    print("logits", logits)
    print("logits", logits.shape)

    log_prob = model.get_log_prob(mock_audio, labels=mock_labels)

    print(log_prob)
