import os
import numpy as np

import models.jigglypuff.distances.base as base
from pipelines.evaluate.query_by_example.model import Setting


class SampleLikelihood(base.Base):

    def __init__(self, export_dir: str, max_distance: float):
        base.Base.__init__(self, export_dir=export_dir)

        self.max_distance = max_distance
        self.keyword_audio = {}

    def register_keyword(self, keyword: str, utterances: np.ndarray):
        if keyword not in self.keyword_audio:
            self.keyword_audio[keyword] = []

        for utterance in utterances:
            self.keyword_audio[keyword].append(utterance)

    def infer_average_score(self, utterance: np.ndarray):
        min_distance, keyword = 1e9, None
        labels, _ = self.get_output(utterance)

        for kw, audios in self.keyword_audio.items():
            score = 0.0
            for audio in audios:
                distance = -self.get_log_prob(audio, labels)
                score += distance / len(audios)

            if score < min_distance:
                min_distance = score
                keyword = kw

        if min_distance < self.max_distance:
            return keyword, keyword, min_distance

        return None, keyword, min_distance

    def infer_most_likely(self, utterance: np.ndarray):
        min_distance, keyword = 1e9, None
        labels, _ = self.get_output(utterance)

        for kw, audios in self.keyword_audio.items():
            for audio in audios:
                distance = -self.get_log_prob(audio, labels)

                if distance < min_distance:
                    min_distance = distance
                    keyword = kw

        if min_distance < self.max_distance:
            return keyword, keyword, min_distance

        return None, keyword, min_distance

    def infer(self, utterance: np.ndarray):
        #return self.infer_average_score(utterance)
        return self.infer_most_likely(utterance)

    def name(self):
        return "Jigglypuff Sample Likelihood"

    def register_setting(self, setting: Setting):
        pass


if __name__ == "__main__":
    model = SampleLikelihood(export_dir=f"{os.getenv('FRIDAY_ROOT')}/mm/data/stp_model/1614070522",
                             max_distance=1000)

    mock_audio_0 = (np.random.normal(-1, 1, 16000) * 10000).astype(np.int16)
    mock_audio_1 = (np.random.normal(1, 1, 16000) * 10000).astype(np.int16)

    model.register_keyword("hi", np.array([mock_audio_0]))

    print(model.infer(mock_audio_1))
    print(model.infer(mock_audio_0))
