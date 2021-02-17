"""QbE Evaluation Pipeline."""
import time
import pathlib
import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
import numpy as np
import random
from pipelines.to_tfexample.google_speech_commands import SUB_PATHS as ALL_KEYWORDS
from tqdm import tqdm
from typing import Iterable

tf.compat.v1.enable_eager_execution()

import argparse
from pipelines.evaluate.query_by_example import model as m
from typing import Iterable


def example_it(examples: str) -> Iterable[tf.train.Example]:
    path_components = examples.split("/")
    suffix = path_components[-1]

    path = "/".join(path_components[:-1])
    files = list(pathlib.Path(path).glob(suffix))

    for file in tqdm(files):
        for example in tf.data.TFRecordDataset(filenames=[str(file)]):
            example = example.numpy()
            yield tf.train.Example.FromString(example)


def sample_keywords(seed: int, n: int, keywords: [str], examples: str) -> Iterable:
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

            audio = tfexample_utils.get_audio(example)
            text = tfexample_utils.get_text(example)
            sample_rate = tfexample_utils.get_sample_rate(example)

            # validation.. should not happen.. if it does.. sorry!
            if text != keyword:
                raise Exception("Text in example did not match that of file_name {text} != {keyword}")

            yield text, audio, sample_rate


def register_keywords(model: m.Model, kas_it: Iterable, window_size: float, sample_rate: int):
    keywords_audio = {}
    window_size_samples = int(window_size * sample_rate)
    for keyword, audio, sr in kas_it:
        if sr != sample_rate:
            raise Exception(f"Sample rate of example not provided {sr} != {sample_rate}")

        padded_audio = list(audio[:window_size_samples])
        padded_audio = padded_audio + [0] * (window_size_samples - len(padded_audio))

        if keyword not in keywords_audio:
            keywords_audio[keyword] = []

        keywords_audio[keyword].append(padded_audio)

    for keyword, audio in keywords_audio.items():
        audio = np.array(audio)
        print(f"{model.name()} registering {keyword} {audio.shape}")
        model.register_keyword(keyword, audio)


def get_all_keywords_ordered(keywords: [str]) -> [str]:
    all_keywords = [k for k in ALL_KEYWORDS]
    for i, keyword in enumerate(keywords):
        j = all_keywords.index(keyword)

        # Swap
        all_keywords[i], all_keywords[j] = all_keywords[j], all_keywords[i]

    return all_keywords


def run_eval(model: m.Model, examples: str, keywords: [str], window_size: str, sample_rate: int):
    all_keywords = get_all_keywords_ordered(keywords)

    # + 1 for 'None', since the model can predict 'None'
    confusion_block = np.zeros((len(keywords) + 1, len(all_keywords)))

    window_size_samples = int(window_size * sample_rate)
    for example in example_it(examples):
        audio = tfexample_utils.get_audio(example)
        text = tfexample_utils.get_text(example)
        sr = tfexample_utils.get_sample_rate(example)

        if sr != sample_rate:
            raise Exception(f"Sample rate of example not provided {sr} != {sample_rate}")

        padded_audio = list(audio[:window_size_samples])
        padded_audio = padded_audio + [0] * (window_size_samples - len(padded_audio))
        padded_audio = np.array(padded_audio)

        prediction = model.infer(padded_audio)

        if prediction:
            confusion_block[keywords.index(prediction), all_keywords.index(text)] += 1
        else:
            confusion_block[len(keywords), all_keywords.index(text)] += 1

    return confusion_block, keywords, all_keywords


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

    args = parser.parse_args()

    model.register_setting(setting=m.Setting(
        sample_rate=args.sample_rate,
        sequence_length=int(args.sample_rate * args.window_size)
    ))

    register_keywords(model=model,
                      kas_it=sample_keywords(seed=args.seed, n=args.n, keywords=keywords, examples=args.examples),
                      window_size=args.window_size,
                      sample_rate=args.sample_rate)

    return run_eval(model=model,
                    examples=args.examples,
                    keywords=keywords,
                    window_size=args.window_size,
                    sample_rate=args.sample_rate)
