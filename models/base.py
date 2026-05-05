import json
import sys
from abc import ABC, abstractmethod
from .prompt import SYSTEM_PROMPT


class BaseClassifier(ABC):
    def __init__(self, key_senders: str, excluded_topics: str):
        self.system_prompt = SYSTEM_PROMPT.format(
            key_senders=key_senders,
            excluded_topics=excluded_topics,
        )

    @abstractmethod
    def classify(self, emails: list[dict]) -> list[dict]:
        """Takes list of email dicts, returns list of critical email dicts."""

    @staticmethod
    def _parse_critical(text: str) -> list[dict]:
        try:
            result = json.loads(text)
            return result.get("critical", [])
        except (json.JSONDecodeError, KeyError) as e:
            print(f"CLASSIFY_PARSE_ERROR: {e}", file=sys.stderr)
            return []

    @staticmethod
    def format_emails(emails: list[dict]) -> str:
        return "\n".join(
            f"{i+1}. Account: {e.get('account', '')} | From: {e['from']} | Subject: {e['subject']} | Snippet: {e.get('snippet', '')}"
            for i, e in enumerate(emails)
        )
