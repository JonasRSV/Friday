"""QbE Evaluation Pipeline."""
import time
import pathlib
import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
import numpy as np
import random
import pandas as pd
import simpleaudio
from pipelines.to_tfexample.google_speech_commands import SUB_PATHS as ALL_KEYWORDS
from pipelines.evaluate.query_by_example import core

tf.compat.v1.enable_eager_execution()

import argparse
from pipelines.evaluate.query_by_example import model as m
from typing import Iterable


def sample_keywords(seed: int, n: int, keywords: [str], examples: str) -> Iterable:
    """Sample n audio files for each keyword using the provided seed from the 'examples' files."""
    path_components = examples.split("/")
    suffix = path_components[-1]

    path = "/".join(path_components[:-1])
    files = list(pathlib.Path(path).glob(suffix))

    random.seed(seed)

    for keyword in keywords:
        # This will crash if a keyword with no file is provided.
        file_with_keyword = random.choice(list(filter(lambda x: keyword in str(x), files)))

        for example in random.choices(list(tf.data.TFRecordDataset(filenames=[str(file_with_keyword)])), k=n):
            example = example.numpy()
            example = tf.train.Example.FromString(example)

            text = tfexample_utils.get_text(example)

            # validation.. should not happen.. if it does.. sorry!
            if text != keyword:
                raise Exception("Text in example did not match that of file_name {text} != {keyword}")

            yield example


def run_eval(model: m.Model, examples: str, keywords: [str], window_size: str, model_sample_rate: int):
    """Run evaluation across a tfexamples dataset."""
    window_size_samples = int(window_size * model_sample_rate)

    utterances, predictions, closest_keywords, distances, latency = [], [], [], [], []
    for example in core.example_it(examples):
        audio = tfexample_utils.get_audio(example)
        text = tfexample_utils.get_text(example)
        sample_rate = tfexample_utils.get_sample_rate(example)

        if sample_rate != model_sample_rate:
            raise Exception(f"Sample rate of example not provided {sample_rate} != {model_sample_rate}")

        padded_audio = list(audio[:window_size_samples])
        padded_audio = padded_audio + [0] * (window_size_samples - len(padded_audio))
        padded_audio = np.array(padded_audio, dtype=np.int16)

        timestamp = time.time()
        prediction, closest_keyword, distance = model.infer(padded_audio)

        #print(text, " -> ", prediction)
        #simpleaudio.play_buffer(padded_audio, num_channels=1, bytes_per_sample=2,
        #                        sample_rate=sample_rate).wait_done()
        #time.sleep(0.25)

        utterances.append(text)
        predictions.append(prediction)
        closest_keywords.append(closest_keyword)
        distances.append(distance)
        latency.append(time.time() - timestamp)

    df = pd.DataFrame({
        "utterance": utterances,
        "prediction": predictions,
        "closest_keyword": closest_keywords,
        "distance": distances,
        "latency": latency

    })

    df["dataset"] = core.Pipelines.GOOGLE_SPEECH_COMMANDS.value
    df["time"] = time.time()
    df["model"] = model.name()

    return df


def run(model: m.Model, keywords: [str]):
    parser = argparse.ArgumentParser()
    parser.add_argument("--examples", required=True, type=str,
                        help="path to examples files, e.g '../tfexample.examples*'")
    parser.add_argument("--n", required=True, type=int,
                        help="Number of examples to be given as training per keyword")
    parser.add_argument("--seed", required=True, type=int,
                        help="Random seed for what keywords")
    parser.add_argument("--window_size", required=True, type=float, help="inference window size, in seconds.")
    parser.add_argument("--sample_rate", required=True, type=int, help="Expected sample_rate of audio.")

    args, _ = parser.parse_known_args()

    model.register_setting(setting=m.Setting(
        sample_rate=args.sample_rate,
        sequence_length=int(args.sample_rate * args.window_size)
    ))

    keywords = core.register_keywords(
        model=model,
        ex_it=sample_keywords(seed=args.seed, n=args.n, keywords=keywords, examples=args.examples),
        keyword_audio_size=args.window_size,
        keyword_audio_sample_rate=args.sample_rate
    )

    return run_eval(model=model,
                    examples=args.examples,
                    keywords=keywords,
                    window_size=args.window_size,
                    model_sample_rate=args.sample_rate)
