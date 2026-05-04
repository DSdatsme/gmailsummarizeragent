import json
import sys
import requests
from .base import BaseClassifier
from .prompt import SYSTEM_PROMPT


class GeminiClassifier(BaseClassifier):
    def __init__(self, api_key: str, model: str, key_senders: str, excluded_topics: str):
        self.api_key = api_key
        self.model = model
        self.system_prompt = SYSTEM_PROMPT.format(
            key_senders=key_senders,
            excluded_topics=excluded_topics,
        )

    def classify(self, emails: list[dict]) -> list[dict]:
        if not emails:
            return []

        payload = {
            "system_instruction": {"parts": [{"text": self.system_prompt}]},
            "contents": [{"parts": [{"text": f"Classify these emails:\n\n{self.format_emails(emails)}"}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0,
                "thinkingConfig": {"thinkingBudget": 0},
            },
        }

        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
            headers={"X-goog-api-key": self.api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()

        try:
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            result = json.loads(text)
            return result.get("critical", [])
        except (KeyError, json.JSONDecodeError) as e:
            print(f"CLASSIFY_PARSE_ERROR: {e}", file=sys.stderr)
            return []
