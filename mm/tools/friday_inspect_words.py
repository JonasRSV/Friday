import lilbrosa
import argparse
import simpleaudio
import random
import numpy as np
from pathlib import Path

tf.compat.v1.enable_eager_execution()

#TODO: 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", type=Path, required=True)

    args = parser.parse_args()
    print(args.prefix)

    for serialized_example in tf.data.TFRecordDataset(filenames=[
        str(random.choice(list(args.prefix.glob("*"))))
    ]):
        example = tf.train.Example()
        example.ParseFromString(serialized_example.numpy())

        anchor = tfexample_dma_utils.get_anchor_audio(example)
        positive = tfexample_dma_utils.get_positive_audio(example)
        negative = tfexample_dma_utils.get_negative_audio(example)

        anchor_text = tfexample_dma_utils.get_anchor_text(example)
        positive_text = tfexample_dma_utils.get_positive_text(example)
        negative_text = tfexample_dma_utils.get_negative_text(example)

        sample_rate = tfexample_dma_utils.get_sample_rate(example)

        print("Anchor", anchor_text)
        simpleaudio.play_buffer(anchor, 1, 2,
                                sample_rate=sample_rate).wait_done()
        print("Positive", positive_text)
        simpleaudio.play_buffer(positive, 1, 2,
                                sample_rate=sample_rate).wait_done()
        print("Negative", negative_text)
        simpleaudio.play_buffer(negative, 1, 2,
                                sample_rate=sample_rate).wait_done()

