"""QbE Usability Evaluation Pipeline."""
import time
import pathlib
import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
import numpy as np
import pandas as pd
import random
from typing import Callable
from pipelines.evaluate.query_by_example import core

tf.compat.v1.enable_eager_execution()

import argparse
from pipelines.evaluate.query_by_example import model as m
from tqdm import tqdm


def run_eval(model_fn: Callable[[], m.Model],
             examples: str,
             window_size: float,
             model_sample_rate: int):
    """Run evaluation across a tfexamples dataset."""
    window_size_samples = int(window_size * model_sample_rate)

    total, keywords_audio = 0, {}
    for example in core.example_it(examples):
        audio = tfexample_utils.get_audio(example)
        text = tfexample_utils.get_text(example)
        sample_rate = tfexample_utils.get_sample_rate(example)

        if sample_rate != model_sample_rate:
            raise Exception(f"Sample rate of example not provided {sample_rate} != {model_sample_rate}")

        padded_audio = list(audio[:window_size_samples])
        padded_audio = padded_audio + [0] * (window_size_samples - len(padded_audio))
        padded_audio = np.array(padded_audio)

        if text not in keywords_audio:
            keywords_audio[text] = []

        keywords_audio[text].append(padded_audio)

        total += 1

    model = model_fn()
    model.register_setting(
        m.Setting(
            sample_rate=model_sample_rate,
            sequence_length=window_size_samples
        )
    )

    f, t, distances = [], [], []
    with tqdm(total=total * total) as progress_bar:
        for kw_1, audios_1 in keywords_audio.items():
            for kw_2, audios_2 in keywords_audio.items():
                for audio_1 in audios_1:
                    for audio_2 in audios_2:
                        f.append(kw_1)
                        t.append(kw_2)
                        distances.append(model.distance(audio_1, audio_2, keyword=kw_2))

                        progress_bar.update(1)

    df = pd.DataFrame({
        "from": f,
        "to": t,
        "distance": distances
    })

    df["time"] = time.time()
    df["model"] = model.name()

    return df


def run(model_fn: Callable[[], m.Model]):
    parser = argparse.ArgumentParser()
    parser.add_argument("--examples", required=True, type=str,
                        help="path to examples files, e.g '../tfexample.examples*'")
    parser.add_argument("--window_size", required=True, type=float, help="inference window size, in seconds.")
    parser.add_argument("--sample_rate", required=True, type=int, help="Expected sample_rate of audio.")

    args, _ = parser.parse_known_args()

    return run_eval(model_fn=model_fn,
                    examples=args.examples,
                    window_size=args.window_size,
                    model_sample_rate=args.sample_rate)
