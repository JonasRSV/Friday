import numpy as np
import shared.tfexample_utils as tfexample_utils
import tensorflow as tf
import argparse
import logging
import simpleaudio

tf.compat.v1.enable_eager_execution()


def manually_filter_on_audio(input_file: str, output_file: str):
    with tf.io.TFRecordWriter(output_file) as writer:
        examples = list(tf.data.TFRecordDataset(filenames=[input_file]))
        for i, serialized_example in enumerate(examples):
            serialized_example = serialized_example.numpy()
            example = tf.train.Example.FromString(serialized_example)

            text = tfexample_utils.get_text(example)
            audio = np.array(tfexample_utils.get_audio(example), dtype=np.int16)
            sample_rate = tfexample_utils.get_sample_rate(example)

            print(f"{i} / {len(examples)} -- Text: ", text)
            simpleaudio.play_buffer(audio, num_channels=1, bytes_per_sample=2, sample_rate=sample_rate)

            if input("d=drop") == "d":
                print("Dropped sample")
                continue

            writer.write(serialized_example)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file",
                        type=str,
                        help="path to file to filter",
                        required=True)
    parser.add_argument("--output_file",
                        type=str,
                        help="path to filtered file",
                        required=True)
    args = parser.parse_args()

    manually_filter_on_audio(args.input_file, args.output_file)
