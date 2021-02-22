import os
import numpy as np
import numba
from models.ditto.algorithms.odtw import dtw

import models.jigglypuff.distances.base as base
from pipelines.evaluate.query_by_example.model import Setting


@numba.jit(nopython=True, fastmath=True)
def discrete(x, y):
    return x == y


class BeamODTW(base.Base):
    def __init__(self, export_dir: str, max_distance: float):
        base.Base.__init__(self, export_dir=export_dir)

        self.max_distance = max_distance
        self.keyword_phoneme_seq = {}

    def register_keyword(self, keyword: str, utterances: np.ndarray):
        if keyword not in self.keyword_phoneme_seq:
            self.keyword_phoneme_seq[keyword] = []

        for utterance in utterances:
            seq, _ = self.get_output(utterance)

            self.keyword_phoneme_seq[keyword].append(seq)

        print(self.keyword_phoneme_seq)

    def infer(self, utterance: np.ndarray):
        min_distance, keyword = 1e9, None
        ut_seq, _ = self.get_output(utterance)
        logits, _ = self.get_logits(utterance)

        for kw, seqs in self.keyword_phoneme_seq.items():
            for seq in seqs:
                x = ut_seq
                template = seq
                sequence_length = len(x)
                template_length = len(template) + 2
                mem = np.zeros((sequence_length, template_length))

                distance = dtw(x=x,
                               template=template,
                               mem=mem,
                               sequence_length=sequence_length,
                               template_length=template_length,
                               distance=discrete)

                if distance < min_distance:
                    min_distance = distance
                    keyword = kw

        if min_distance < self.max_distance:
            return keyword, keyword, min_distance

        return None, keyword, min_distance

    def name(self):
        return "Jigglypuff BeamODTW"

    def register_setting(self, setting: Setting):
        pass


if __name__ == "__main__":
    model = BeamODTW(export_dir=f"{os.getenv('FRIDAY_ROOT')}/mm/data/stp_model/1613990506",
                     max_distance=1000)

    mock_audio = (np.random.rand(16000) * 30000).astype(np.int16)
    output, output_shape = model.get_output(mock_audio)

    print("output_shape", output_shape)
    print("output", output)

    logits, logits_shape = model.get_logits(mock_audio)

    print("logits_shape", logits_shape)
    print("logits", logits)
    print("logits", logits.shape)
