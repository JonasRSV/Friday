import tensorflow as tf
import argparse
from tqdm import tqdm
from typing import Iterable
import pathlib
import numpy as np
from models.jigglypuff.distances.beam_odtw import BeamODTW
import shared.tfexample_utils as tfexample_utils

from dtw import dtw

def discrete(x, y):
    #if x == 0 or y == 0:
     #   return 0

    return 1 - int(x == y)

tf.compat.v1.enable_eager_execution()

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
        for example in tqdm(list(tf.data.TFRecordDataset(filenames=[str(file)]))):
            example = example.numpy()
            yield tf.train.Example.FromString(example)


def phoneme_error_rate(model, it):

    total_samples = 0
    total_err = 0
    for example in it:
        audio = np.array(tfexample_utils.get_audio(example))
        labels = np.array(tfexample_utils.get_phoneme_labels(example))


        prediction, _ = model.get_output(audio)
        #print("prediction", predition, "labels", labels)

        error, _, _, _ = dtw(labels, prediction, dist=discrete)

        total_err += error / len(labels)
        total_samples += 1


        print("error", total_err / total_samples)








if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--examples", required=True, type=str, help="path to examples files, e.g '../tfexample.examples*'")
    parser.add_argument("--export_dir", type=str, required=True)
    args, _ = parser.parse_known_args()

    model = BeamODTW(export_dir=args.export_dir, max_distance=0.0)

    phoneme_error_rate(model, example_it(args.examples))

