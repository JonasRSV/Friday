import numpy as np
import os

from models.bulbasaur.inference.base import Base
from pipelines.evaluate.query_by_example.model import Setting


class Simple(Base):
    def __init__(self, export_dir: str, max_distance: float):
        Base.__init__(self, export_dir=export_dir)
        self.max_distance = max_distance

        self.keywords = []
        self.embeddings = []

    def name(self):
        return "Bulbasaur Simple"

    def infer_most_likely(self, utterance: np.ndarray):
        print("embeddings", self.embeddings.shape)
        similarities, _ = self.get_similarities(self.embeddings, utterance)

        print("similarities", similarities)

        distance = 1 - np.max(similarities)
        prediction = self.keywords[np.argmax(similarities)]

        if distance < self.max_distance:
            return prediction, distance, prediction

        return None, distance, prediction

    def infer(self, utterance: np.ndarray):
        return self.infer_most_likely(utterance)

    def register_keyword(self, keyword: str, utterances: np.ndarray):
        self.embeddings = list(self.embeddings)
        for utterance in utterances:
            projection, _ = self.get_projection(utterance)
            self.embeddings.append(projection)

        self.embeddings = np.array(self.embeddings)

        self.keywords.extend([keyword] * len(utterances))

    def register_setting(self, setting: Setting):
        pass


if __name__ == "__main__":
    model = Simple(export_dir=f"{os.getenv('FRIDAY_ROOT')}/mm/data/bulbasaur_model/1614849325",
                   max_distance=1000)

    mock_audio_0 = (np.random.normal(-1, 1, 16000) * 10000).astype(np.int16)
    mock_audio_1 = (np.random.normal(1, 1, 16000) * 10000).astype(np.int16)
    mock_audio_2 = (np.random.normal(10, 1, 16000) * 1000).astype(np.int16)

    model.register_keyword("hi", np.array([mock_audio_0, mock_audio_1]))

    print(model.infer(mock_audio_0))
    print(model.infer(mock_audio_1))
    print(model.infer(mock_audio_2))
