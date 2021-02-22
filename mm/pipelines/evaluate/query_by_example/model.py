import numpy as np
from abc import ABC, abstractmethod


class Setting:
    def __init__(self, sample_rate: int, sequence_length: int):
        self.sample_rate = sample_rate
        self.sequence_length = sequence_length


class Model(ABC):

    @abstractmethod
    def register_setting(self, setting: Setting):
        """Register the setting this evaluation runs in.

        This gives models access to some perhaps necessary information for preprocessing,
        and also a chance to crash early if they are not implemented for this setting.

        This function is called first, before everything else.
        """
        raise NotImplementedError(f"'register_setting' have not been implemented for {self.__class__}")

    @abstractmethod
    def register_keyword(self, keyword: str, utterances: np.ndarray):
        """Register a keyword to a model.

        keyword: string identifier of keyword - e.g 'Hello'
        utterances: MxN matrix of the 16bit samples, M is the number of recordings and N the number of samples.
        """
        raise NotImplementedError(f"'register_keyword' have not been implemented for {self.__class__}")

    @abstractmethod
    def infer(self, utterance: np.ndarray):
        """Infer the keyword, if any, in the utterance.

        utterance: A N-vector containing the 16bit samples.

        Returns
            (A, B, C)
            A: the 'keyword' identifier provided to 'register_keyword' or 'None' if no known keyword is present.
            B: the 'keyword' closest to the utterance
            C: the distance to the keyword closest to the utterance
        """
        raise NotImplementedError(f"'infer' have not been implemented for {self.__class__}")

    @abstractmethod
    def name(self):
        """Name of current model"""
        raise NotImplementedError(f"'name' have not been implemented for {self.__class__}")
