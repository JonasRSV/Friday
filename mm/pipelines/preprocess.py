import sys
import os

# Some systems dont use the launching directory as root
sys.path.append(os.getcwd())

import json
import tensorflow as tf
import argparse
from pipelines.preprocessing import core
from pipelines.preprocessing.audio_padding import AudioPadding
from pipelines.preprocessing.lowercase_text import TextLowerCase
from pipelines.preprocessing.crop_audio import IdentifySpeechAndCrop
from pipelines.preprocessing.label_map_labler import Labler
from tqdm import tqdm

tf.compat.v1.enable_eager_execution()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--source",
                        type=str,
                        help="Prefix of sharded file",
                        required=True)
    parser.add_argument("--sink_prefix",
                        type=str,
                        help="Prefix of output sharded file",
                        required=True)
    parser.add_argument('--label_map_path', type=str, dest="label_map_path",
                        help="Path to json label map for labels", required=True)
    parser.add_argument('--maximum_clip_length', type=int, dest="maximum_clip_length",
                        help="All audio clips with length longer than 'maximum_clip_length' will be dropped",
                        default=2)

    args = parser.parse_args()

    with open(args.label_map_path, "r") as label_map_file:
        doFns = [
            IdentifySpeechAndCrop(length_of_speech=args.maximum_clip_length),
            # LengthFilter(max_length=args.maximum_clip_length, min_length=0.0),
            TextLowerCase(),
            AudioPadding(length=args.maximum_clip_length),
            Labler(label_map=json.load(label_map_file)),
        ]

    jobs, memory_to_process = core.build_jobs_with_file_information(source_prefix=args.source)

    expected_MB_per_file = 100
    sinks = core.create_sinks(prefix=args.sink_prefix, n=int(memory_to_process / expected_MB_per_file))
    jobs = [job.add_preprocessing_fn(doFns=doFns).add_sinks(sinks) for job in jobs]

    with tqdm(total=memory_to_process) as progress_bar:
        # TODO look into creating some kind of custom lock so we can run this across multiple processes
        # The current problem is that by naively multiprocessing this we will run into race conditions when writing
        # to file. Also it is unclear if the tensorflow writers can be pickled and used with python MP.
        # Need to figure out what the bottleneck is, perhaps it is IO and in that case threading might be enough.
        for job in jobs:
            job.execute()
            progress_bar.update(n=job.size)
