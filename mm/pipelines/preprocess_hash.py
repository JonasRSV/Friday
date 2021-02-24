import sys
import os

# Some systems dont use the launching directory as root
sys.path.append(os.getcwd())

import tensorflow as tf
import argparse
from pipelines.preprocessing.uppercase_text import TextUpperCase
from pipelines.preprocessing.chunker import Chunker
from pipelines.preprocessing.audio_padding import AudioPadding
from pipelines.preprocessing.hash_labler import HashLabeler
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
    parser.add_argument('--maximum_clip_length', type=float,
                        help="All audio clips with length (seconds) longer than 'maximum_clip_length' will be chunked",
                        default=2)
    parser.add_argument('--chunk_stride', type=float,
                        help="The stride (seconds) used to chunk audio clips - clips are split striding 'chunk_stride",
                        default=1)
    parser.add_argument("--expected_output_file_size", type=int, help="File size in MB",
                        default=100)

    args = parser.parse_args()
    print(args)

    doFns = [
        Chunker(max_clip_length=args.maximum_clip_length, chunk_stride=args.chunk_stride),
        TextUpperCase(),
        AudioPadding(length=args.maximum_clip_length),
        HashLabeler(),
    ]

    jobs, memory_to_process = core.build_jobs_with_file_information(source_prefix=args.source)

    expected_MB_per_file = args.expected_output_file_size
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
