from abc import ABC, abstractmethod


class BaseClassifier(ABC):
    @abstractmethod
    def classify(self, emails: list[dict]) -> list[dict]:
        """Takes list of email dicts, returns list of critical email dicts."""

    @staticmethod
    def format_emails(emails: list[dict]) -> str:
        return "\n".join(
            f"{i+1}. Account: {e.get('account', '')} | From: {e['from']} | Subject: {e['subject']} | Snippet: {e.get('snippet', '')}"
            for i, e in enumerate(emails)
        )
