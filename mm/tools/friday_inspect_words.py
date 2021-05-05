import librosa
import time
from pipelines.preprocessing.audio_augmentations import AudioAugmentations
from pipelines.preprocessing.random_bipadding import bipadding
import argparse
import simpleaudio
import random
import numpy as np
from pathlib import Path

#TODO: 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", type=Path, required=True)
    parser.add_argument("--augment", action="store_true")
    parser.add_argument("--sample_rate", type=int, default=16000)
    args = parser.parse_args()

    words = list(args.prefix.glob("*"))
    print("words", len(words))

    augmentor = AudioAugmentations(args.sample_rate)

    while True:
        word = random.choice(words)
        print("word", word)

        audio_file = random.choice(list(word.glob("*")))
        print("file", audio_file)

        content, sr = librosa.load(audio_file, sr=args.sample_rate)
        content = (content * 2**15).astype(np.int16)

        content = bipadding(2, content, sr)
        if args.augment:
            content = augmentor.do(content)

        print("content", content)

        simpleaudio.play_buffer(content, 1, 2,
                                sample_rate=args.sample_rate).wait_done()

        time.sleep(1)

