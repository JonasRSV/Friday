import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
import pathlib
from tqdm import tqdm
from pipelines.preprocessing.abstract_preprocess_fn import PreprocessFn
from typing import List

def extract_phoneme(phoneme: str) -> str:
    """This takes a ARPABET phoneme and returns the consonant or vowel representation.

    This strips away any 'Stress' or 'Auxiliary symbols' as described in https://en.wikipedia.org/wiki/ARPABET
    """
    for i in range(len(phoneme)):
        if not phoneme[i].isalpha():
            return phoneme[:i]

    return phoneme


class ARPABETPhonemeLabeler(PreprocessFn):
    """This phoneme labeler assumes a dictionary formatted as

    WORD PHONEME PHONEME ...
    WORD PHONEME PHONEME ...

    Each word is on its own line and it is followed by the white-space separated phonemes that
    represents it.

    This is the format of the librispeech ARPABET dictionary:
    http://www.openslr.org/resources/11/librispeech-lexicon.txt
    """

    def __init__(self, phoneme_dict_path: pathlib.Path):
        self.word_phonemes_mapping = {}
        self.phonemes = set()

        with open(str(phoneme_dict_path), "r") as phoneme_dict_file:
            lines = phoneme_dict_file.readlines()
            print(f"word phoneme dictionary contains {len(lines)} lines")
            number_of_collisions = 0
            for line in tqdm(lines,
                             "Preprocessing phoneme dictionary"):
                chunks = line.strip().split()

                word = chunks[0].strip()
                phonemes = chunks[1:]

                word_phonemes = list(map(extract_phoneme, phonemes))
                if word not in self.word_phonemes_mapping:
                    self.word_phonemes_mapping[word] = word_phonemes
                else:
                    number_of_collisions += 1

                self.phonemes = self.phonemes.union(word_phonemes)

        print(f"Found {len(self.word_phonemes_mapping)} words")
        print(f"There were {number_of_collisions} collisions")
        print(f"Found {len(self.phonemes)} phonemes")

        self.phonemes = list(self.phonemes)
        self.phonemes.sort()
        self.phoneme_labels = {}
        for label, phoneme in enumerate(self.phonemes):
            print(f"{label}: {phoneme}")
            self.phoneme_labels[phoneme] = label

        # See https://dl.acm.org/doi/pdf/10.1145/1143844.1143891 about blank label
        # See https://www.tensorflow.org/versions/r1.15/api_docs/python/tf/nn/ctc_loss_v2 why we set blank as 0
        self.word_boundary_label = len(self.phoneme_labels)
        print(f"Adding {self.word_boundary_label} as a word boundary label")

        self.kept_samples = 0
        self.dropped_samples = 0

    def do(self, example: tf.train.Example) -> List[tf.train.Example]:
        text = tfexample_utils.get_text(example)

        # Assume some silence in beginning
        labels = [self.word_boundary_label]
        for word in text.split(" "):
            word = word.strip()
            if word in self.word_phonemes_mapping:
                for phoneme in self.word_phonemes_mapping[word]:
                    labels.append(self.phoneme_labels[phoneme])
            else:
                self.dropped_samples += 1
                return []

            # Assume silence after word and in the end
            labels.append(self.word_boundary_label)

        self.kept_samples += 1
        return [tfexample_utils.set_phoneme_labels(example=example,
                                                   labels=labels)]
