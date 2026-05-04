"""
One-time script to get Gmail OAuth2 refresh token for an account.
Usage: python auth_setup.py <account_name>
Example: python auth_setup.py personal
Requires credentials.json downloaded from GCP Console (OAuth2 Desktop App).
"""
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

account = sys.argv[1] if len(sys.argv) > 1 else "default"

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)

env_key = f"GMAIL_{account.upper().replace('-', '_')}_REFRESH_TOKEN"
print(f"\nAdd this to config.env or Secret Manager for account '{account}':")
print(f"{env_key}={creds.refresh_token}")
print(f"\n(GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET are shared — only set them once)")
