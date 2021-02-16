from abc import ABC, abstractmethod


class Metric(ABC):

    @abstractmethod
    def update(self, pred_utterance: [str], pred_at_time: [int], utterances: [str], at_time: [int], total: int):
        """Update the metric with the result of a task."""
        raise NotImplementedError(f"'update' have not been implemented for {self.__class__}")

    @abstractmethod
    def summarize(self):
        """Summarize the metric"""
        raise NotImplementedError(f"'summarize' have not been implemented for {self.__class__}")
