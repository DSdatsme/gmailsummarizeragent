# Gmail Filer

Fetches emails from multiple Gmail accounts, classifies them for criticality using an LLM, and sends a consolidated notification. Runs automatically on a schedule via GitHub Actions.

## How it works

```
Gmail API (5 accounts)
        │
        ▼
   Fetch emails
  (last N hours)
        │
        ▼
  LLM Classifier
 (Gemini / OpenRouter / Azure)
        │
        ▼
  Notification channel
      (Telegram)
```

1. **Fetch** — pulls unread emails from each Gmail account via the Gmail API using OAuth2 refresh tokens. Only emails from the last `LOOKBACK_HOURS` are considered.
2. **Classify** — sends all emails in a single prompt to an LLM. The model returns only the emails it considers critical, along with a reason. Emails from `KEY_SENDERS` are always marked critical. Topics in `EXCLUDED_TOPICS` are always skipped.
3. **Notify** — sends a consolidated Telegram message listing the critical emails with subject, sender, account, and reason.

## Project structure

```
main.py               # orchestrator
gmail.py              # Gmail API fetcher
auth_setup.py         # one-time OAuth2 token generator
models/
  openrouter.py       # OpenRouter classifier (default)
  azure_openai.py     # Azure OpenAI classifier
  gemini.py           # Gemini direct API classifier
channels/
  telegram.py         # Telegram notification channel
config.env.example    # copy to config.env for local runs
.github/workflows/
  run.yml.example     # reference GitHub Actions workflow
```

## Setup

### 1. GCP — create OAuth2 credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
2. Create an **OAuth 2.0 Client ID** (Desktop app type)
3. Download `credentials.json` and place it in the project root
4. Enable the **Gmail API** for your project

### 2. Generate refresh tokens

Run once per Gmail account, **on your local machine** (requires a browser for the OAuth consent screen):

```bash
pip install -r requirements.txt
python auth_setup.py personal     # opens browser for OAuth consent
python auth_setup.py work
# repeat for each account
```

Each run prints a `GMAIL_<NAME>_REFRESH_TOKEN=...` value. Save these — you'll need them in step 4.

### 3. Choose a model provider

| Provider | Env vars needed | Notes |
|---|---|---|
| `gemini` | `GEMINI_API_KEY`, `MODEL` | Recommended. Fast, generous free tier. |
| `openrouter` | `OPENROUTER_API_KEY`, `MODEL` | 1M free requests/month. Many models. |
| `azure` | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT` | Use if you have an Azure subscription. |

### 4. Configure

Copy `config.env.example` to `config.env` and fill in the values:

```bash
cp config.env.example config.env
```

Key settings:

| Variable | Description |
|---|---|
| `MODEL_PROVIDER` | `gemini`, `openrouter`, or `azure` |
| `GMAIL_ACCOUNTS` | Comma-separated account names, e.g. `personal,work` |
| `LOOKBACK_HOURS` | How far back to fetch emails (e.g. `13` for twice-daily runs) |
| `KEY_SENDERS` | Domains/addresses always marked critical, e.g. `toptal.com` |
| `EXCLUDED_TOPICS` | Topics to always skip, e.g. `newsletter, LinkedIn job alert` |

### 5. Run locally

```bash
python main.py
```

## GitHub Actions setup (recommended)

The workflow runs on a **private repo** that references this public code repo. This keeps secrets and run logs private.

### Why two repos?

GitHub Actions logs are visible to anyone for public repos. Using a private runner repo means your email subjects, sender names, and any error output stay private.

### Steps

1. Create a **private** GitHub repo (e.g. `gmail-filer-runner`)
2. Copy `.github/workflows/run.yml.example` into that repo as `.github/workflows/run.yml`
3. Update the `repository:` field in the checkout step to point to this repo
4. Set the following **Variables** (Settings → Secrets and variables → Actions → Variables):

| Variable | Example value |
|---|---|
| `MODEL_PROVIDER` | `gemini` |
| `MODEL` | `gemini-flash-latest` |
| `LOOKBACK_HOURS` | `13` |
| `NOTIFY_CHANNELS` | `telegram` |
| `GMAIL_ACCOUNTS` | `personal,work` |
| `GMAIL_CLIENT_ID` | from `credentials.json` |
| `AZURE_OPENAI_ENDPOINT` | your Azure endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT` | your deployment name |
| `KEY_SENDERS` | `example.com` |
| `EXCLUDED_TOPICS` | `newsletter, marketing` |
| `TELEGRAM_CHAT_ID` | your Telegram chat ID |

5. Set the following **Secrets** (Settings → Secrets and variables → Actions → Secrets):

| Secret | Description |
|---|---|
| `GMAIL_CLIENT_SECRET` | from `credentials.json` |
| `GMAIL_<NAME>_REFRESH_TOKEN` | one per account from step 2 |
| `GEMINI_API_KEY` | Gemini API key |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI key |
| `TELEGRAM_BOT_TOKEN` | from @BotFather |

6. Adjust the cron schedule in the workflow file to your preferred time
7. Trigger a manual run to verify everything works

## Adding a new Gmail account

```bash
python auth_setup.py newaccount
# add GMAIL_NEWACCOUNT_REFRESH_TOKEN to config.env or GitHub Secrets
# add "newaccount" to GMAIL_ACCOUNTS
```

## Extending

**Add a notification channel:** implement `channels/base.py:BaseChannel` and register it in `channels/__init__.py`.

**Switch models:** set `MODEL_PROVIDER` and the corresponding API key. No code changes needed.
