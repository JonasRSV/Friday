# Some systems dont use the launching directory as root
import sys
import os

sys.path.append(os.getcwd())

import pathlib
import argparse
import multiprocessing as mp
from typing import List
import sox
import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
from tqdm import tqdm


class Config:
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate


def locate_transcriptions(chapter_root: pathlib.Path):
    transcriptions = list(chapter_root.glob("*.trans.txt"))

    if len(transcriptions) > 0:
        return transcriptions[0]
    else:
        return None


def convert_chapter(chapter_root: pathlib.Path,
                    transformer: sox.Transformer,
                    writer: tf.io.TFRecordWriter,
                    config: Config):
    transcription = locate_transcriptions(chapter_root)
    if not transcription:
        print(f"Found no transcription in {chapter_root}, skipping...")
        return

    with open(str(transcription), "r") as transcription_file:
        for line in transcription_file.readlines():
            line = line.strip()
            end_of_index = line.find(" ")

            file_name = line[:end_of_index].strip() + ".flac"
            file = chapter_root / file_name

            text = line[end_of_index:].strip()

            resampled_audio = transformer.build_array(
                input_filepath=str(file), sample_rate_in=config.sample_rate)
            example = tfexample_utils.create_example(
                audio=resampled_audio,
                text=text,
                sample_rate=config.sample_rate
            )

            writer.write(example.SerializeToString())


def convert_speaker(speaker_root: pathlib.Path, prefix: str, config: Config, suffix: str):
    transformer = sox.Transformer()
    with tf.io.TFRecordWriter(f"{prefix}.{suffix}") as writer:
        for chapter_id in speaker_root.glob("*"):
            if chapter_id.stem.isnumeric():
                convert_chapter(chapter_id, transformer, writer, config)
            else:
                print(f"{chapter_id} is not numeric, skipping...")


def convert_dataset(dataset_root: pathlib.Path, prefix: str, config: Config, dataset_id: int):
    for speaker_n, speaker_id in tqdm(list(enumerate(dataset_root.glob("*")))):
        if speaker_id.stem.isnumeric():
            convert_speaker(speaker_id, prefix, config, f"{dataset_id}-{speaker_n}")
        else:
            print(f"{speaker_id} is not numeric, skipping...")


def convert(root: pathlib.Path, datasets: List[str], prefix: str, config: Config):
    """Convert the 'datasets' to tfexamples"""
    for dataset_id, dataset in enumerate(datasets, 1):
        dataset_path = root / dataset

        if dataset_path.is_dir():
            convert_dataset(dataset_root=dataset_path, prefix=prefix, config=config, dataset_id=dataset_id)
        else:
            print(f"{dataset_path} is not a directory, skipping..")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-libri_root", type=pathlib.Path,
                           help="Path to the root directory of the LibriSpeech dataset")
    argparser.add_argument("-output_prefix", type=str, help="prefix (including path) of output tfexamples")
    argparser.add_argument("--sample_rate", type=int, default=8000, help="Sample rate of audio")

    datasets_to_convert = [
        "train-clean-100",
        "train-clean-360",
        "train-other-500"
    ]

    args = argparser.parse_args()

    convert(args.libri_root,
            datasets_to_convert,
            args.output_prefix,
            config=Config(sample_rate=args.sample_rate))
