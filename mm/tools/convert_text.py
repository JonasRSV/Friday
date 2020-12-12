import numpy as np
import shared.tfexample_utils as tfexample_utils
import tensorflow as tf
import pathlib
import argparse
import logging
from tqdm import tqdm

tf.compat.v1.enable_eager_execution()


def convert_label(input_directory: str, output_directory: str, label_from: str, label_to: str):
    converted = 0

    output_directory = pathlib.Path(output_directory)
    for file in tqdm(list(pathlib.Path(input_directory).glob("*"))):
        with tf.io.TFRecordWriter(str(output_directory / file.name)) as writer:
            for serialized_example in tf.data.TFRecordDataset(filenames=[str(file)]):
                serialized_example = serialized_example.numpy()
                example = tf.train.Example.FromString(serialized_example)

                text = tfexample_utils.get_text(example)
                audio = np.array(tfexample_utils.get_audio(example), dtype=np.int16)
                sample_rate = tfexample_utils.get_sample_rate(example)

                updated_text = label_to if text == label_from else text

                if updated_text != text:
                    converted += 1

                writer.write(
                    tfexample_utils.create_example(
                        text=updated_text,
                        audio=audio,
                        sample_rate=sample_rate
                    ).SerializeToString())

    print("Converted", converted)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_directory",
                        type=str,
                        help="path to input directory",
                        required=True)
    parser.add_argument("--output_directory",
                        type=str,
                        help="path to output directory",
                        required=True)
    parser.add_argument("--convert_from",
                        type=str,
                        help="What label to convert",
                        required=True)
    parser.add_argument("--convert_to",
                        type=str,
                        help="What to convert label to ",
                        required=True)
    args = parser.parse_args()

    convert_label(args.input_directory, args.output_directory, args.convert_from, args.convert_to)
