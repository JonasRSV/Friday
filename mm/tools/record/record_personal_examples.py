import shared.tfexample_utils as tfexample_utils
import random
import alsaaudio
import tensorflow as tf
import argparse
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import simpleaudio

tf.compat.v1.enable_eager_execution()


def record_audio(file_prefix: str, clip_length: float, sample_rate: int, device: str, text: str):
    suffix = random.randint(0, 10000000)
    file_name = f"{file_prefix}.personal.{suffix}"
    while pathlib.Path(file_name).is_file():
        suffix = random.randint(0, 10000000)
        file_name = f"{file_prefix}.personal.{suffix}"

    datawriter = tf.io.TFRecordWriter(path=file_name)

    print(f"Welcome to data recorder, to stop press <C-c> at anytime and your files will be saved")
    print(f"you have provided: {text} -- all recordings well be assumed to contain this")

    # recording.pause(False)
    try:
        while True:
            input(f"Press enter to start recording -- will record for {clip_length} seconds")

            recording = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE,
                                      mode=alsaaudio.PCM_NORMAL,
                                      rate=sample_rate,
                                      channels=1,
                                      periodsize=int(sample_rate * clip_length),
                                      device=device)

            recording.setperiodsize(int(sample_rate * clip_length))

            audio_frames = []
            total_length = 0
            while total_length < int(sample_rate * (clip_length + 0.5)):
                length, data = recording.read()

                audio_frames.append(data)
                total_length += length

            recording.close()
            audio_data = b''.join(audio_frames)

            audio_data = np.fromstring(audio_data, dtype="int16")
            audio_data = audio_data[int(sample_rate * 0.5):int(sample_rate * (clip_length + 0.5))]

            example = tfexample_utils.create_example(
                text=text,
                audio=list(map(int, audio_data)),
                sample_rate=sample_rate
            )

            simpleaudio.play_buffer(audio_data, num_channels=1, bytes_per_sample=2, sample_rate=sample_rate)

            datawriter.write(example.SerializeToString())
    except KeyboardInterrupt:
        print(f"Interrupt detected, data is stored to: {file_name}")

    datawriter.close()


def record_background(file_prefix: str, clip_length: float, sample_rate: int, device: str):
    suffix = random.randint(0, 10000000)
    file_name = f"{file_prefix}.personal.{suffix}"
    while pathlib.Path(file_name).is_file():
        suffix = random.randint(0, 10000000)
        file_name = f"{file_prefix}.personal.{suffix}"

    datawriter = tf.io.TFRecordWriter(path=file_name)

    print(f"Welcome to data recorder, to stop press <C-c> at anytime and your files will be saved")
    try:
        while True:
            recording = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE,
                                      mode=alsaaudio.PCM_NORMAL,
                                      rate=sample_rate,
                                      channels=1,
                                      periodsize=int(sample_rate * clip_length),
                                      device=device)

            recording.setperiodsize(int(sample_rate * clip_length))

            audio_frames = []
            total_length = 0
            # Add 0.5 seconds of recording to avoid annoying clip sound for some mics when they turn on
            while total_length < int(sample_rate * (clip_length + 0.5)):
                length, data = recording.read()

                audio_frames.append(data)
                total_length += length

            recording.close()
            audio_data = b''.join(audio_frames)

            audio_data = np.fromstring(audio_data, dtype="int16")
            # drop first 0.5 seconds
            audio_data = audio_data[int(sample_rate * 0.5):int(sample_rate * (clip_length + 0.5))]

            example = tfexample_utils.create_example(
                text="[UNK]",
                audio=list(map(int, audio_data)),
                sample_rate=sample_rate
            )

            print("Stored")

            datawriter.write(example.SerializeToString())
    except KeyboardInterrupt:
        print(f"Interrupt detected, data is stored to: {file_name}")

    datawriter.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_prefix",
                        type=str,
                        help="Path to goldfish audio file",
                        required=True)
    parser.add_argument("--sample_rate",
                        type=int,
                        help="sample rate to record with",
                        required=True)
    parser.add_argument("--clip_length",
                        type=float,
                        help="length in seconds to record",
                        required=True)
    parser.add_argument("--text",
                        type=str,
                        help="text assumed to be in each recording",
                        required=True)
    parser.add_argument("--background",
                        type=bool,
                        help="text assumed to be in each recording",
                        default=False)

    parser.add_argument("--device",
                        type=str,
                        help="Device to use for recording")

    args = parser.parse_args()

    if args.background:
        record_background(file_prefix=args.file_prefix,
                          clip_length=args.clip_length,
                          sample_rate=args.sample_rate,
                          device=args.device)
    else:
        record_audio(file_prefix=args.file_prefix,
                     clip_length=args.clip_length,
                     sample_rate=args.sample_rate,
                     device=args.device,
                     text=args.text)
