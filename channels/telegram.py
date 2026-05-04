import sys
import requests
from .base import BaseChannel


class TelegramChannel(BaseChannel):
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def notify(self, critical_emails: list[dict]) -> None:
        lines = "\n\n".join(
            f"• `{e.get('account', '')}` — *{e['subject']}*\n  {e['from']} _({e.get('reason', '')})_"
            for e in critical_emails
        )
        text = f"*📬 Critical Emails*\n\n{lines}"

        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                json={"chat_id": self.chat_id, "parse_mode": "Markdown", "text": text},
                timeout=10,
            )
            if not resp.ok:
                print("TELEGRAM_FAIL: non-OK response", file=sys.stderr)
        except requests.RequestException:
            print("TELEGRAM_FAIL: request error", file=sys.stderr)
