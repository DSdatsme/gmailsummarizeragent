import json
import sys
from openai import AzureOpenAI
from .base import BaseClassifier


class AzureOpenAIClassifier(BaseClassifier):
    def __init__(self, endpoint: str, api_key: str, deployment: str, key_senders: str, excluded_topics: str):
        super().__init__(key_senders=key_senders, excluded_topics=excluded_topics)
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-01",
        )
        self.deployment = deployment

    def classify(self, emails: list[dict]) -> list[dict]:
        if not emails:
            return []

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Classify these emails:\n\n{self.format_emails(emails)}"},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )

        try:
            result = json.loads(response.choices[0].message.content)
            return result.get("critical", [])
        except (json.JSONDecodeError, KeyError) as e:
            print(f"CLASSIFY_PARSE_ERROR: {e}", file=sys.stderr)
            return []
