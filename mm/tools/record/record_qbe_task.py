"""
Tool for recording datasets used for 'online' evaluation
This script produces a tensorflow example with the fields

audio: int64list (16bit audio, each int is a whole sample)
sample_rate: int64list # a list containing one scalar, the sample_rate of the audio
utterances: byteslist (a '-' separated list of the uttered keywords)
at_time: int64list (For each entry in the list there is a utterance value signifying
at around what 'sample' the KW was uttered)

"""

import shared.tfexample_utils as tfexample_utils
import sys
import termios
import tty
import argparse
import tensorflow as tf
import random
import pathlib
import numpy as np
import threading
import alsaaudio
import simpleaudio
import time
from typing import List
from queue import Queue, Empty

tf.compat.v1.enable_eager_execution()


def create_example(
        audio: List[int],
        sample_rate: int,
        utterances: str,
        at_time: List[int]) -> tf.train.Example:
    features = tf.train.Features(
        feature=dict(audio=tfexample_utils.int64list_feature(audio),
                     utterances=tfexample_utils.bytes_feature(utterances),
                     sample_rate=tfexample_utils.int64list_feature([sample_rate]),
                     at_time=tfexample_utils.int64list_feature(at_time)))

    return tf.train.Example(features=features)


def getch():
    """For reading character press without 'enter'"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def get_writer():
    suffix = random.randint(0, 10000000)
    file_name = f"/tmp/tfexamples.online-eval.{suffix}"
    while pathlib.Path(file_name).is_file():
        suffix = random.randint(0, 10000000)
        file_name = f"tfexamples.online-eval.{suffix}"

    print("Saving too..", file_name)
    return tf.io.TFRecordWriter(path=file_name)


class DatasetRecorder:
    def __init__(self, sample_rate: int, device: str = "default"):
        self.sample_rate = sample_rate
        self.current_sample = 0

        self.device = device
        self.recording_thread = None
        self.recording = False

        self.audio_data = None
        self.listening_terminal = False


    def run_recording(self):
        print("Starting recording")
        recorder = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE,
                                 mode=alsaaudio.PCM_NORMAL,
                                 rate=self.sample_rate,
                                 channels=1,
                                 periodsize=int(self.sample_rate * 0.5),
                                 device=self.device)
        self.recording = True

        audio_frames = []
        while self.recording:
            length, data = recorder.read()

            audio_frames.append(data)
            self.current_sample += length

        recorder.close()
        audio_data = b''.join(audio_frames)

        self.audio_data = np.fromstring(audio_data, dtype="int16")

    def run(self, keywords: List[str]):
        print("quit=q    ", end="")
        for index, kw in enumerate(keywords):
            print(f"'{kw}'={index} ", end="")
        print()

        self.recording_thread = threading.Thread(target=self.run_recording)
        self.recording_thread.start()

        char_queue = Queue()

        def fill_queue():
            while self.listening_terminal:
                ch = getch()
                char_queue.put(ch)

                if not ch.isnumeric():
                    break

        self.listening_terminal = True
        self.term_input_thread = threading.Thread(target=fill_queue)
        self.term_input_thread.start()

        utterances = []
        at_time = []

        timestamp, last_word = time.time(), ""
        while True:

            try:
                inp = char_queue.get(block=True, timeout=1)

                if inp.isnumeric():
                    utterances.append(keywords[int(inp)])
                    at_time.append(self.current_sample)

                    print("Registered", keywords[int(inp)], end="                                    \r")

                    last_word = keywords[int(inp)]
                    timestamp = time.time()
                else:
                    print("Quitting")
                    break
            except Empty:
                print("Registered", last_word, int(time.time() - timestamp), "seconds ago",
                      end="                                                     \r")

        self.recording = False
        self.recording_thread.join()

        self.listening_terminal = False
        self.term_input_thread.join()

        print("Writing to file...")
        writer = get_writer()
        example = create_example(audio=self.audio_data,
                                 sample_rate=self.sample_rate,
                                 utterances="-".join(utterances),
                                 at_time=at_time)

        writer.write(example.SerializeToString())
        writer.close()
        print("Done!")

        print("Replaying keywords, press <C-c> to stop at any time")

        for sample, keyword in zip(at_time, utterances):
            print(f"Playing {keyword} at {sample}")
            simpleaudio.play_buffer(self.audio_data[sample - self.sample_rate: sample + self.sample_rate],
                                    num_channels=1,
                                    bytes_per_sample=2,
                                    sample_rate=self.sample_rate)
            time.sleep(2)

        print("All done@")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample_rate", type=int, default=8000)

    args = parser.parse_args()

    # keywords = [
    #    "tänd ljuset",
    #    "släck ljuset",
    #    "sluta",
    #    "friday",
    #    "vad är klockan"
    # ]

    keywords = [
        "time",
        "stop",
        "night",
        "morning",
        "illuminate",
        "alarm"
    ]

    DatasetRecorder(sample_rate=args.sample_rate).run(keywords)
