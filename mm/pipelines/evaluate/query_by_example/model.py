import numpy as np
from abc import ABC, abstractmethod


class Model(ABC):

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
            the 'keyword' identifier provided to 'register_keyword' or 'None' if no known keyword is present.
        """
        raise NotImplementedError(f"'infer' have not been implemented for {self.__class__}")

    @abstractmethod
    def name(self):
        """Name of current model"""
        raise NotImplementedError(f"'name' have not been implemented for {self.__class__}")
