import numpy as np
import os
from models.bulbasaur.inference.preprocess import fix_loudness

from models.bulbasaur.inference.base import Base
from pipelines.evaluate.query_by_example.model import Setting


class Simple(Base):
    def distance(self, a: np.ndarray, b: np.ndarray, **kwargs):
        a = fix_loudness(a)
        b = fix_loudness(b)

        a, _ = self.get_projection(a)

        return self.get_distances(embeddings=[a], audio=b)[0]

    def __init__(self, export_dir: str, max_distance: float):
        Base.__init__(self, export_dir=export_dir)
        self.max_distance = max_distance

        self.keywords = []
        self.embeddings = []
        self.keyword_norm = []

    def name(self):
        return "DDL-COS"

    def infer_most_likely(self, utterance: np.ndarray):
        distances = self.get_distances(self.embeddings, utterance)
        distances = distances #/ self.keyword_norm

        #similarities, _ = self.get_similarities(self.embeddings, utterance)
        #distances = 1 - similarities

        prediction = self.keywords[np.argmin(distances)]
        distance = np.min(distances)

        if distance < self.max_distance:
            return prediction, prediction, distance

        return None, prediction, distance

    def infer_average(self, utterance: np.ndarray):
        distances = self.get_distances(self.embeddings, utterance)

        kw_distances = {}
        for i, kw in enumerate(self.keywords):
            if kw not in kw_distances:
                kw_distances[kw] = {
                    "count": 0,
                    "value": 0
                }

            kw_distances[kw]["value"] += distances[i]
            kw_distances[kw]["count"] += 1

        ranking = [(kw, distance["value"] / distance["count"]) for kw, distance in kw_distances.items()]
        ranking.sort(key=lambda x: x[1])

        prediction, distance = ranking[0]

        if distance < self.max_distance:
            return prediction, prediction, distance

        return None, prediction, distance

    def infer(self, utterance: np.ndarray):
        utterance = fix_loudness(utterance)
        #return self.infer_average(utterance)
        return self.infer_most_likely(utterance)

    def register_keyword(self, keyword: str, utterances: np.ndarray):
        utterances = fix_loudness(utterances)

        self.embeddings = list(self.embeddings)
        for utterance in utterances:
            projection, _ = self.get_projection(utterance)
            self.embeddings.append(projection)

        self.embeddings = np.array(self.embeddings)

        self.keywords.extend([keyword] * len(utterances))

        self.keyword_norm = list(self.keyword_norm)
        self.keyword_norm.extend([len(keyword)] * len(utterances))
        self.keyword_norm = np.array(self.keyword_norm)

    def register_setting(self, setting: Setting):
        pass


if __name__ == "__main__":
    model = Simple(export_dir=f"{os.getenv('FRIDAY_ROOT')}/mm/data/bulbasaur_model/ddl_apr_6",
                   max_distance=1000)

    mock_audio_0 = (np.random.normal(-1, 1, 16000) * 10000).astype(np.int16)
    mock_audio_1 = (np.random.normal(1, 1, 16000) * 10000).astype(np.int16)
    mock_audio_2 = (np.random.normal(10, 1, 16000) * 1000).astype(np.int16)

    model.register_keyword("hi", np.array([mock_audio_0, mock_audio_1]))
    model.register_keyword("ho", np.array([mock_audio_2]))

    print(model.infer(mock_audio_0))
    print(model.infer(mock_audio_1))
    print(model.infer(mock_audio_2))
