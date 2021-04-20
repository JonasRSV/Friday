import os
import numpy as np
import numba
from models.ditto.algorithms.odtw import dtw
from models.jigglypuff.distances.preprocess import fix_loudness

import models.jigglypuff.distances.base as base
from pipelines.evaluate.query_by_example.model import Setting


@numba.jit(nopython=True, fastmath=True)
def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


@numba.jit(nopython=True, fastmath=True)
def entropy(x, y):
    """A measure of entropy of the two distributions x and y."""
    # KL Divergence
    # Good
    return (np.log(softmax(y) / softmax(x)) * softmax(y)).sum()

    # Same as Gaussian PosterioGrams DTW paper https://www.researchgate.net/profile/James-Glass-3/publication/224096804_Unsupervised_spoken_keyword_spotting_via_segmental_DTW_on_Gaussian_Posteriorgrams/links/02e7e53b41b829dc8d000000/Unsupervised-spoken-keyword-spotting-via-segmental-DTW-on-Gaussian-Posteriorgrams.pdf
    # return -np.log(softmax(x) @ softmax(y))
    # No good :I
    # return (np.log(softmax(x) / softmax(y)) * softmax(x)).sum()

    # Jensen Shannon Distance (Maybe)
    # x = softmax(x)
    # y = softmax(y)
    # m = (x + y) / 2

    # a = (np.log(y / m) * y).sum()
    # b = (np.log(x / m) * x).sum()

    # return a + b

    ## Total Variation Distance (Nah)
    # x = softmax(x)
    # y = softmax(y)

    # x[-1] = 0
    # y[-1] = 0

    # x[0] = 0
    # y[0] = 0

    # return np.abs(x - y).max()

    # return np.sqrt(np.square(x - y).sum())
    # return (x - y).min()

    # Cosine
    # x_norm = x / np.sqrt(x @ x)
    # y_norm = y / np.sqrt(y @ y)

    # return 1 - x_norm @ y_norm


class PosteriogramsODTW(base.Base):
    def distance(self, a: np.ndarray, b: np.ndarray, **kwargs):
        a = fix_loudness(a)
        b = fix_loudness(b)

        a, _ = self.get_logits(a)
        b, _ = self.get_logits(b)

        return self.ghost_dtw(a, b)

    def __init__(self, export_dir: str, max_distance: float):
        base.Base.__init__(self, export_dir=export_dir)

        self.max_distance = max_distance
        self.keyword_logitss = {}

    def register_keyword(self, keyword: str, utterances: np.ndarray):
        utterances = fix_loudness(utterances)
        if keyword not in self.keyword_logitss:
            self.keyword_logitss[keyword] = []

        for utterance in utterances:
            seq, _ = self.get_logits(utterance)

            print(seq.shape)
            self.keyword_logitss[keyword].append(seq)

        print(self.keyword_logitss)

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
                   distance=entropy)

    def infer_min_avg_distance(self, utterance: np.ndarray):
        min_distance, keyword = 1e9, None
        ut_logits, _ = self.get_logits(utterance)

        for kw, logitss in self.keyword_logitss.items():
            score = 0
            for logits in logitss:
                score += self.ghost_dtw(ut_logits, logits)

            if score < min_distance:
                min_distance = score
                keyword = kw

        if min_distance < self.max_distance:
            return keyword, keyword, min_distance

        return None, keyword, min_distance

    def infer_min_distance(self, utterance: np.ndarray):
        min_distance, keyword = 1e9, None
        ut_logits, _ = self.get_logits(utterance)

        for kw, logitss in self.keyword_logitss.items():
            for logits in logitss:
                distance = self.ghost_dtw(ut_logits, logits) / len(kw)

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
        return "STP-PKL"

    def register_setting(self, setting: Setting):
        pass


if __name__ == "__main__":
    print(entropy(np.random.rand(10), np.random.rand(10)))
    model = PosteriogramsODTW(export_dir=f"{os.getenv('FRIDAY_ROOT')}/mm/data/stp_model/1614070522",
                              max_distance=1000)

    mock_audio_0 = (np.random.normal(-1, 1, 16000) * 10000).astype(np.int16)
    mock_audio_1 = (np.random.normal(2, 1, 16000) * 10000).astype(np.int16)

    model.register_keyword("hi", np.array([mock_audio_0]))

    print(model.infer(mock_audio_1))
    print(model.infer(mock_audio_0))
