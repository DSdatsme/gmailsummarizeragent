import json
import sys
from openai import OpenAI
from .base import BaseClassifier

_SYSTEM_PROMPT = """\
You are an email triage assistant. Classify each email as CRITICAL or NOT CRITICAL.

An email is NEVER CRITICAL if it is about:
{excluded_topics}

An email is CRITICAL only if NONE of the above exclusions apply AND ANY of the following are true:
- Urgent or time-sensitive: contains a deadline, "ASAP", a meeting needing a response, or an expiring offer
- From a key person (match by name or email substring): {key_senders}
- Explicitly requires an action: reply needed, approval, decision, or form to fill
- Direct personal outreach from a recruiter about a specific role (NOT automated job alerts, NOT application status updates, NOT LinkedIn digests or notifications)

Respond with JSON: {{"critical": [{{"account": "...", "from": "...", "subject": "...", "reason": "one short phrase"}}]}}
If no critical emails, respond with: {{"critical": []}}
"""


class OpenRouterClassifier(BaseClassifier):
    def __init__(self, api_key: str, model: str, key_senders: str, excluded_topics: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model
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
            model=self.model,
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
