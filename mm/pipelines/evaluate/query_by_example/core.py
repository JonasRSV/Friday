from typing import Iterable
from tqdm import tqdm
import shared.tfexample_utils as tfexample_utils
from pipelines.evaluate.query_by_example import model as m
from enum import Enum
import pathlib
import tensorflow as tf
import numpy as np

tf.compat.v1.enable_eager_execution()


class Pipelines(Enum):
    PERSONAL = "P"
    GOOGLE_SPEECH_COMMANDS = "GSC"


def example_it(examples: str, progress=True) -> Iterable[tf.train.Example]:
    path_components = examples.split("/")
    suffix = path_components[-1]

    path = "/".join(path_components[:-1])
    files = list(pathlib.Path(path).glob(suffix))

    if progress:
        iterator = tqdm(files)
    else:
        iterator = files

    for file in iterator:
        for example in tf.data.TFRecordDataset(filenames=[str(file)]):
            example = example.numpy()
            yield tf.train.Example.FromString(example)


def register_keywords(model: m.Model,
                      ex_it: Iterable[tf.train.Example],
                      keyword_audio_size: float, keyword_audio_sample_rate: int):
    keywords_audio = {}
    for example in ex_it:
        audio = tfexample_utils.get_audio(example)
        text = tfexample_utils.get_text(example)
        sample_rate = tfexample_utils.get_sample_rate(example)

        # Pad audio files to window_size
        padded_audio_length = int(keyword_audio_size * keyword_audio_sample_rate)
        audio = audio[:padded_audio_length]
        audio = audio + [0] * (padded_audio_length - len(audio))

        if text not in keywords_audio:
            keywords_audio[text] = []

        keywords_audio[text].append(audio)

        # If audio files got different sample_rates the pipeline gets UB, here we crash instead.
        if keyword_audio_sample_rate != sample_rate:
            raise Exception(f"Files contain different sample rates {keyword_audio_sample_rate} != {sample_rate}")

    for keyword, audio in keywords_audio.items():
        np_audio = np.array(audio)
        print(f"{model.name()} registering {keyword} - {np_audio.shape}")

        print("audio", type(np_audio))
        model.register_keyword(keyword, np_audio)

    return list(keywords_audio.keys())
