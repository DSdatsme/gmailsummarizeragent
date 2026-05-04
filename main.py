import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "config.env")

from gmail import GmailFetcher
from models import get_classifier
from channels import get_channels


def get_fetchers() -> list[GmailFetcher]:
    accounts = [a.strip() for a in os.environ.get("GMAIL_ACCOUNTS", "default").split(",")]
    lookback_hours = int(os.environ.get("LOOKBACK_HOURS", "13"))
    client_id = os.environ["GMAIL_CLIENT_ID"]
    client_secret = os.environ["GMAIL_CLIENT_SECRET"]
    fetchers = []
    for account in accounts:
        fetchers.append(GmailFetcher(
            account=account,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=os.environ[f"GMAIL_{account.upper().replace('-', '_')}_REFRESH_TOKEN"],
            lookback_hours=lookback_hours,
        ))
    return fetchers


def main():
    fetchers = get_fetchers()
    classifier = get_classifier()
    channels = get_channels()

    all_emails = []
    for fetcher in fetchers:
        all_emails.extend(fetcher.fetch())

    critical = classifier.classify(all_emails)

    if critical:
        for channel in channels:
            channel.notify(critical)

    print(f"{len(all_emails)} emails checked across {len(fetchers)} account(s), {len(critical)} critical, {len(channels) if critical else 0} notifications sent.")


if __name__ == "__main__":
    main()
