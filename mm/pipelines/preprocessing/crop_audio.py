import tensorflow as tf
import shared.tfexample_utils as tfexample_utils
from pipelines.preprocessing.abstract_preprocess_fn import PreprocessFn
from typing import List


def voice_start(audio: [int], sample_rate: int):
    # TODO(jonasrsv):
    return 0


class IdentifySpeechAndCrop(PreprocessFn):
    """A doFn for cropping audio into at most 'length_of_speech'.

        'length_of_speech' is in the unit of seconds

    """

    def __init__(self, length_of_speech: float):
        self.length_of_speech = length_of_speech

    def do(self, example: tf.train.Example) -> List[tf.train.Example]:
        sample_rate = tfexample_utils.get_sample_rate(example)
        audio = tfexample_utils.get_audio(example)

        # If audio is longer than speech we crop
        if len(audio) / sample_rate >= self.length_of_speech:
            start = voice_start(audio, sample_rate)

            samples_in_speech = int(self.length_of_speech * sample_rate)
            cropped_audio = audio[start: start + samples_in_speech]

            return [tfexample_utils.set_audio(example=example,
                                              audio=cropped_audio)]

        # If audio is already short enough we do nothing
        return [example]
