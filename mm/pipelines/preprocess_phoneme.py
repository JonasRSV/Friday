import sys
import os

# Some systems dont use the launching directory as root
sys.path.append(os.getcwd())

import pathlib
import tensorflow as tf
import argparse
from pipelines.preprocessing.uppercase_text import TextUpperCase
from pipelines.preprocessing.phoneme_dict_labler import ARPABETPhonemeLabeler
from pipelines.preprocessing import core
from tqdm import tqdm

tf.compat.v1.enable_eager_execution()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--source",
                        type=str,
                        help="Prefix of input sharded file",
                        required=True)
    parser.add_argument("--sink_prefix",
                        type=str,
                        help="Prefix of output sharded file",
                        required=True)
    parser.add_argument('--phoneme_dictionary_path', type=pathlib.Path,
                        help="Path to phoneme dictionary", required=True)

    args = parser.parse_args()

    labeler = ARPABETPhonemeLabeler(phoneme_dict_path=args.phoneme_dictionary_path)
    doFns = [
        # All should be uppercase already in LibriSpeech
        # TextUpperCase(),
        labeler
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

    print("Dropped samples", labeler.dropped_samples)
    print("Kept samples", labeler.kept_samples)
