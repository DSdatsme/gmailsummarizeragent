from openai import OpenAI
from .base import BaseClassifier


class OpenRouterClassifier(BaseClassifier):
    def __init__(self, api_key: str, model: str, key_senders: str, excluded_topics: str):
        super().__init__(key_senders=key_senders, excluded_topics=excluded_topics)
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model

    def classify(self, emails: list[dict]) -> list[dict]:
        if not emails:
            return []

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Classify these emails:\n\n{self.format_emails(emails)}"},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )

        return self._parse_critical(response.choices[0].message.content)
