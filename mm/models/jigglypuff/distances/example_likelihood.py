import os
import numpy as np

import models.jigglypuff.distances.base as base
from pipelines.evaluate.query_by_example.model import Setting
from models.jigglypuff.distances.preprocess import fix_loudness

class ExampleLikelihood(base.Base):

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

        print(self.keyword_phoneme_seq)

    def infer_average_score(self, utterance: np.ndarray):
        min_distance, keyword = 1e9, None

        for kw, seqs in self.keyword_phoneme_seq.items():
            score = 0.0
            for seq in seqs:
                distance = -self.get_log_prob(utterance, seq)
                score += distance / len(seqs)

            if score < min_distance:
                min_distance = score
                keyword = kw

        if min_distance < self.max_distance:
            return keyword, keyword, min_distance

        return None, keyword, min_distance

    def infer_most_likely(self, utterance: np.ndarray):
        min_distance, keyword = 1e9, None

        for kw, seqs in self.keyword_phoneme_seq.items():
            for seq in seqs:
                distance = -self.get_log_prob(utterance, seq) - len(seq)

                if distance < min_distance:
                    min_distance = distance
                    keyword = kw

        if min_distance < self.max_distance:
            return keyword, keyword, min_distance

        return None, keyword, min_distance

    def infer(self, utterance: np.ndarray):
        utterance = fix_loudness(utterance)
        #return self.infer_average_score(utterance)
        return self.infer_most_likely(utterance)

    def name(self):
        return "STP-EL"

    def register_setting(self, setting: Setting):
        pass


if __name__ == "__main__":
    model = ExampleLikelihood(export_dir=f"{os.getenv('FRIDAY_ROOT')}/mm/data/stp_model/1614070522",
                              max_distance=1000)

    mock_audio_0 = (np.random.normal(-1, 1, 16000) * 10000).astype(np.int16)
    mock_audio_1 = (np.random.normal(1, 1, 16000) * 10000).astype(np.int16)

    model.register_keyword("hi", np.array([mock_audio_0]))

    print(model.infer(mock_audio_1))
    print(model.infer(mock_audio_0))
