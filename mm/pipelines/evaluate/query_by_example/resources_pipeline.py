"""QbE Resource evaluation Pipeline."""
import pandas as pd
import tensorflow as tf
import numpy as np
import time
from typing import Callable
from tqdm import tqdm

tf.compat.v1.enable_eager_execution()

import argparse
from pipelines.evaluate.query_by_example import model as m


def run(model_fn: Callable[[], m.Model], K: int, N: int):
    """Evaluate latency of a model for different number of examples.

    model: Model to evaluate
    K: maximum number of examples
    N: inferences per example
    """

    Ks, latencies = [], []
    for k in tqdm(range(1, K)):
        audio = np.random.normal(0, 100, size=(k, 16000)).astype(np.int16)

        model = model_fn()
        model.register_setting(
            m.Setting(
                sample_rate=8000,
                sequence_length=16000
            )
        )
        model.register_keyword(str(k), audio)

        utterance = np.random.normal(0, 100, 16000).astype(np.int16)

        for n in range(N):


            timestamp = time.time()
            model.infer(utterance)

            if n > 1:
                Ks.append(k)
                latencies.append(time.time() - timestamp)

    df = pd.DataFrame({
        "K": Ks,
        "latency": latencies
    })

    model = model_fn()

    df["model"] = model.name()
    df["timestamp"] = time.time()

    return df






