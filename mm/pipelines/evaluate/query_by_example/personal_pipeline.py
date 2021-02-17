"""QbE Evaluation Pipeline."""
import time
import pathlib
import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
import pipelines.evaluate.query_by_example.task_tfexample_utils as task_tfexample_utils
from pipelines.evaluate.query_by_example.metrics.personal.accuracy import Accuracy
import numpy as np
from tqdm import tqdm

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


def register_keywords(model: m.Model, examples: str, window_size: int, base_sample_rate: int):
    keywords_audio = {}
    for example in example_it(examples):
        audio = tfexample_utils.get_audio(example)
        text = tfexample_utils.get_text(example)
        sample_rate = tfexample_utils.get_sample_rate(example)

        # Pad audio files to window_size
        padded_audio_length = int(window_size * sample_rate)
        audio = audio[:padded_audio_length]
        audio = audio + [0] * (len(audio) - padded_audio_length)

        if text not in keywords_audio:
            keywords_audio[text] = []

        keywords_audio[text].append(audio)

        # If audio files got different sample_rates the pipeline gets UB, here we crash instead.
        if base_sample_rate != sample_rate:
            raise Exception(f"Files contain different sample rates {base_sample_rate} != {sample_rate}")

    for keyword, audio in keywords_audio.items():
        audio = np.array(audio)
        print(f"{model.name()} registering {keyword} - {audio.shape}")

        model.register_keyword(keyword, audio)

    return model


def simulate_task(model: m.Model, audio: np.ndarray, sample_rate: int, window_size: float, window_stride: float):
    window_size_samples = int(window_size * sample_rate)
    window_stride_samples = int(window_stride * sample_rate)

    utterances, at_time = [], []
    current_sample, total_predictions = 0, 0
    with tqdm(total=audio.size) as progress_bar:
        while current_sample + window_size_samples < audio.size:
            total_predictions += 1
            utterance = model.infer(audio[current_sample: current_sample + window_size_samples])

            if utterance:
                utterances.append(utterance)
                at_time.append(current_sample + (window_size_samples / 2))

            current_sample += window_stride_samples

            progress_bar.update(window_stride_samples)

    return utterances, at_time, total_predictions


def run_eval(model: m.Model, tasks: str, window_size: float, window_stride: float, sample_rate: int):
    metrics = [
        Accuracy(window=int(sample_rate * window_size) * 2)
    ]

    run_times = []
    for task in example_it(tasks):
        audio = np.array(task_tfexample_utils.get_audio(task))
        utterances = task_tfexample_utils.get_utterances(task).split("-")
        at_time = task_tfexample_utils.get_at_time(task)
        sr = task_tfexample_utils.get_sample_rate(task)

        # If audio files got different sample_rates the pipeline gets UB, here we crash instead.
        if sr != sample_rate:
            raise Exception(f"Files contain different sample rates {sr} != {sample_rate}")

        timestamp = time.time()
        pred_utterances, pred_at_time, total_predictions = simulate_task(model,
                                                                         audio,
                                                                         sample_rate,
                                                                         window_size,
                                                                         window_stride)

        time_normalizing = len(audio) / (sample_rate * window_stride)
        run_times.append((time.time() - timestamp) / time_normalizing)

        for x in metrics:
            x.update(pred_utterances=pred_utterances, pred_at_time=pred_at_time,
                     utterances=utterances, at_time=at_time, total=total_predictions)

    run_times = np.array(run_times)
    print(f"average run-time = {run_times.mean()}")
    for x in metrics:
        x.summarize()


def run(model: m.Model):
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", required=True, type=str, help="path to task files, e.g '../tfexample.task*'")
    parser.add_argument("--examples", required=True, type=str,
                        help="path to examples files, e.g '../tfexample.examples*'")
    parser.add_argument("--window_size", required=True, type=float, help="inference window size, in seconds.")
    parser.add_argument("--window_stride", required=True, type=float, help="inference window stride, in seconds.")
    parser.add_argument("--sample_rate", required=True, type=int, help="Expected sample_rate of audio.")

    args = parser.parse_args()

    print(f"Tasks: {args.tasks}")
    print(f"Examples: {args.examples}")
    print(f"Window Size: {args.window_size}")
    print(f"Window Stride: {args.window_stride}")
    print(f"Sample Rate: {args.sample_rate}")

    model.register_setting(setting=m.Setting(
        sample_rate=args.sample_rate,
        sequence_length=int(args.sample_rate * args.window_size)
    ))

    register_keywords(model,
                      examples=args.examples,
                      window_size=args.window_size,
                      base_sample_rate=args.sample_rate)
    run_eval(model,
             tasks=args.tasks,
             window_size=args.window_size,
             window_stride=args.window_stride,
             sample_rate=args.sample_rate)
