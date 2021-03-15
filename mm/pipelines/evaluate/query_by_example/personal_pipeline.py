"""QbE Evaluation Pipeline."""
import time
import pandas as pd
import tensorflow as tf
import pipelines.evaluate.query_by_example.task_tfexample_utils as task_tfexample_utils
from pipelines.evaluate.query_by_example import core
import numpy as np
from tqdm import tqdm

tf.compat.v1.enable_eager_execution()

import argparse
from pipelines.evaluate.query_by_example import model as m


def simulate_task(model: m.Model,
                  audio: np.ndarray,
                  sample_rate: int,
                  window_size: float,
                  window_stride: float):
    """Simulate running the model on audio of the task file.

    Returns:
        For each instance the predicted label or 'None' and the sample in the middle of the prediction window.
    """
    window_size_samples = int(window_size * sample_rate)
    window_stride_samples = int(window_stride * sample_rate)

    utterances, at_time, closest_keywords, distances, latency = [], [], [], [], []
    with tqdm(total=audio.size) as progress_bar:
        current_sample = 0
        while current_sample + window_size_samples < audio.size:
            timestamp = time.time()
            utterance, closest_keyword, distance = model.infer(audio[current_sample:
                                                                     current_sample + window_size_samples])

            closest_keywords.append(closest_keyword)
            distances.append(distance)
            latency.append(time.time() - timestamp)

            utterances.append(utterance)
            at_time.append(current_sample + (window_size_samples / 2))

            current_sample += window_stride_samples
            progress_bar.update(window_stride_samples)

    return utterances, at_time, closest_keywords, distances, latency


def align_labels(task: str,
                 keywords: [str],
                 pred_ut: [str],
                 pred_at_time: [int],
                 ut: [str],
                 at_time: [int],
                 window: float):
    """Aligns predictions and labels into two dataframes

    Given two sequences

    (hello, 1), (cool, 100), (well, 129)
    (hello, 10), (well, 128)

    and a window size

    a utterance is considered correct if there is a utterance of the same keyword in the labels within 'window'


    Returns:
        P, L

        P: pd.DataFrame
        L: pd.DataFrame


        P: (len(pred_ut) x (len(keywords) + 4))
        L: (len(ut) x (len(keywords) + 4))

        + 4 because we're adding 'None' label, task-id, time and 'label'


    Each dataframe contains
    'id' 'utterance' 'time' '{keyword_1}' '{keyword_2}' .. '{keyword_m}'

    where the number at entry '{keyword_x}' is the number of times it was predicted in the window of 'utterance'


    The first contains it for the predictions, the second for the labels.
    """
    # Add None label
    keywords = [k for k in keywords] + ['None']
    pred_ut = list(map(str, pred_ut))
    ut = list(map(str, ut))

    p_len = len(pred_ut)
    l_len = len(ut)

    # Dynamic typing ftw
    P = [[task] + [pred_ut[p]] + [pred_at_time[p]] + ([0] * len(keywords)) for p in range(p_len)]
    L = [[task] + [ut[l]] + [at_time[l]] + ([0] * len(keywords)) for l in range(l_len)]

    for p in range(p_len):
        for l in range(l_len):
            matches_time = abs(pred_at_time[p] - at_time[l]) < window

            if matches_time:
                P[p][keywords.index(ut[l]) + 3] += 1
                L[l][keywords.index(pred_ut[p]) + 3] += 1
            else:
                P[p][keywords.index('None') + 3] += 1

    p_df = pd.DataFrame(P, columns=["id", "prediction", "time"] + keywords)

    best_guess_utterances = []
    for i in range(p_len):
        all_but_none = keywords[:-1]
        occurrences = p_df[all_but_none].iloc[i]
        if np.max(occurrences) > 0:
            best_guess_utterances.append(keywords[np.argmax(occurrences)])
        else:
            best_guess_utterances.append("None")

    p_df["utterance"] = best_guess_utterances

    return p_df, pd.DataFrame(L, columns=["id", "utterance", "time"] + keywords)


def filter_labels(keywords: [str], ut: [str], at_time: [str]):
    """Filter ut and at_time to only contain occurrences in keywords."""
    k = set(keywords)

    ut_n, at_time_n = [], []
    for i in range(len(ut)):
        if ut[i] in k:
            ut_n.append(ut[i])
            at_time_n.append(at_time[i])

    return ut_n, at_time_n


def run_eval(model: m.Model,
             keywords: [str],
             tasks: str,
             window_size: float,
             window_stride: float,
             model_sample_rate: int):
    """Run model evaluation on all tasks"""
    pred_data, label_data = [], []
    for task_id, task in enumerate(core.example_it(tasks)):
        audio = np.array(task_tfexample_utils.get_audio(task))
        utterances = task_tfexample_utils.get_utterances(task).split("-")
        at_time = task_tfexample_utils.get_at_time(task)
        sample_rate = task_tfexample_utils.get_sample_rate(task)

        utterances, at_time = filter_labels(keywords, ut=utterances, at_time=at_time)

        # If audio files got different sample_rates the pipeline gets UB, here we crash instead.
        if sample_rate != model_sample_rate:
            raise Exception(f"Files contain different sample rates {sample_rate} != {model_sample_rate}")

        pred_utterances, pred_at_time, closest_keywords, distances, latency = simulate_task(model,
                                                                                            audio,
                                                                                            sample_rate,
                                                                                            window_size,
                                                                                            window_stride)

        p, l = align_labels(task=str(task_id),
                            keywords=keywords,
                            pred_ut=pred_utterances,
                            pred_at_time=pred_at_time,
                            ut=utterances,
                            at_time=at_time,
                            window=1 * model_sample_rate)

        p["task"] = task
        p["latency"] = latency
        p["model"] = model.name()
        p["closest_keyword"] = closest_keywords
        p["distance"] = distances
        p["dataset"] = core.Pipelines.PERSONAL.value
        p["time"] = time.time()

        l["model"] = model.name()
        l["dataset"] = core.Pipelines.PERSONAL.value
        l["time"] = time.time()

        pred_data.append(p)
        label_data.append(l)

    return pd.concat(pred_data), pd.concat(label_data)


def run(model: m.Model):
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", required=True, type=str, help="path to task files, e.g '../tfexample.task*'")
    parser.add_argument("--examples", required=True, type=str,
                        help="path to examples files, e.g '../tfexample.examples*'")
    parser.add_argument("--window_size", required=True, type=float, help="inference window size, in seconds.")
    parser.add_argument("--window_stride", required=True, type=float, help="inference window stride, in seconds.")
    parser.add_argument("--sample_rate", required=True, type=int, help="Expected sample_rate of audio.")

    args, _ = parser.parse_known_args()

    print(f"Tasks: {args.tasks}")
    print(f"Examples: {args.examples}")
    print(f"Window Size: {args.window_size}")
    print(f"Window Stride: {args.window_stride}")
    print(f"Sample Rate: {args.sample_rate}")

    model.register_setting(setting=m.Setting(
        sample_rate=args.sample_rate,
        sequence_length=int(args.sample_rate * args.window_size)
    ))

    keywords = core.register_keywords(
        model=model,
        ex_it=core.example_it(args.examples),
        keyword_audio_size=args.window_size,
        keyword_audio_sample_rate=args.sample_rate
    )

    return run_eval(model,
                    keywords=keywords,
                    tasks=args.tasks,
                    window_size=args.window_size,
                    window_stride=args.window_stride,
                    model_sample_rate=args.sample_rate), keywords
