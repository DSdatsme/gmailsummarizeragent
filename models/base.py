from abc import ABC, abstractmethod


class BaseClassifier(ABC):
    @abstractmethod
    def classify(self, emails: list[dict]) -> list[dict]:
        """Takes list of email dicts, returns list of critical email dicts."""
