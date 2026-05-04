from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


class GmailFetcher:
    _SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self, account: str, client_id: str, client_secret: str, refresh_token: str, lookback_hours: int):
        self.account = account
        self.lookback_hours = lookback_hours
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=self._SCOPES,
        )
        creds.refresh(Request())
        self.service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    def fetch(self) -> list[dict]:
        emails = []
        page_token = None
        query = f"newer_than:{self.lookback_hours}h"

        while True:
            kwargs = {"userId": "me", "q": query, "maxResults": 50}
            if page_token:
                kwargs["pageToken"] = page_token

            result = self.service.users().messages().list(**kwargs).execute()

            for msg in result.get("messages", []):
                detail = self.service.users().messages().get(
                    userId="me", id=msg["id"], format="metadata",
                    metadataHeaders=["From", "Subject"],
                ).execute()
                headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
                emails.append({
                    "account": self.account,
                    "from": headers.get("From", ""),
                    "subject": headers.get("Subject", ""),
                    "snippet": detail.get("snippet", ""),
                })

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return emails
