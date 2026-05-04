import json
import sys
from openai import AzureOpenAI
from .base import BaseClassifier
from .openrouter import _SYSTEM_PROMPT


class AzureOpenAIClassifier(BaseClassifier):
    def __init__(self, endpoint: str, api_key: str, deployment: str, key_senders: str, excluded_topics: str):
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-01",
        )
        self.deployment = deployment
        self.system_prompt = _SYSTEM_PROMPT.format(
            key_senders=key_senders,
            excluded_topics=excluded_topics,
        )

    def classify(self, emails: list[dict]) -> list[dict]:
        if not emails:
            return []

        email_list = "\n".join(
            f"{i+1}. Account: {e.get('account', '')} | From: {e['from']} | Subject: {e['subject']} | Snippet: {e.get('snippet', '')}"
            for i, e in enumerate(emails)
        )

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Classify these emails:\n\n{email_list}"},
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
