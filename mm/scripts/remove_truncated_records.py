import argparse
import tensorflow as tf
import sys
import os
from pathlib import Path
from tqdm import tqdm
tf.compat.v1.enable_eager_execution()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)

    args = parser.parse_args()

    continue_dropping = False
    for file in tqdm(list(args.source.glob("*"))):
        try:
            for i, example in enumerate(tf.data.TFRecordDataset(filenames=[str(file)])):
                continue
        except Exception as e:
            if not continue_dropping:
                print("got exception", e, file)
                print("cont?")
                if "y" not in input():
                    sys.exit(0)

                continue_dropping = True

            os.remove(file)




