import os
from .base import BaseChannel
from .telegram import TelegramChannel


def get_channels() -> list[BaseChannel]:
    names = os.environ.get("NOTIFY_CHANNELS", "telegram").split(",")
    channels = []
    for name in names:
        name = name.strip()
        if name == "telegram":
            channels.append(TelegramChannel(
                bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
                chat_id=os.environ["TELEGRAM_CHAT_ID"],
            ))
        else:
            raise ValueError(f"Unknown channel: {name}")
    return channels
