#!/usr/bin/env bash
# Usage: GCP_PROJECT_ID=my-project ./deploy.sh
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?GCP_PROJECT_ID is required}"
REGION="${GCP_REGION:-us-central1}"
IMAGE="gcr.io/${PROJECT_ID}/gmail-filer-cloud"
JOB_NAME="gmail-filer"
SA_EMAIL="gmail-filer@${PROJECT_ID}.iam.gserviceaccount.com"

echo "--- Building and pushing image ---"
gcloud builds submit --tag "$IMAGE" --project "$PROJECT_ID"

echo "--- Creating secrets in Secret Manager (skips if already exists) ---"
# Collect per-account refresh token secret names from GMAIL_ACCOUNTS env var
ACCOUNT_SECRETS=""
ACCOUNT_SECRET_REFS=""
for account in $(echo "${GMAIL_ACCOUNTS:-personal}" | tr ',' ' '); do
  secret_name="GMAIL_$(echo "$account" | tr '[:lower:]' '[:upper:]')_REFRESH_TOKEN"
  gcloud secrets describe "$secret_name" --project "$PROJECT_ID" &>/dev/null \
    || gcloud secrets create "$secret_name" --replication-policy automatic --project "$PROJECT_ID"
  ACCOUNT_SECRET_REFS="${ACCOUNT_SECRET_REFS}${secret_name}=${secret_name}:latest,"
done

for secret in OPENROUTER_API_KEY GMAIL_CLIENT_ID GMAIL_CLIENT_SECRET GMAIL_ACCOUNTS \
              TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID KEY_SENDERS EXCLUDED_TOPICS LOOKBACK_HOURS NOTIFY_CHANNELS MODEL; do
  gcloud secrets describe "$secret" --project "$PROJECT_ID" &>/dev/null \
    || gcloud secrets create "$secret" --replication-policy automatic --project "$PROJECT_ID"
done

echo "--- Deploying Cloud Run Job ---"
gcloud run jobs deploy "$JOB_NAME" \
  --image "$IMAGE" \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --service-account "$SA_EMAIL" \
  --set-secrets "\
OPENROUTER_API_KEY=OPENROUTER_API_KEY:latest,\
GMAIL_CLIENT_ID=GMAIL_CLIENT_ID:latest,\
GMAIL_CLIENT_SECRET=GMAIL_CLIENT_SECRET:latest,\
GMAIL_ACCOUNTS=GMAIL_ACCOUNTS:latest,\
${ACCOUNT_SECRET_REFS}\
TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN:latest,\
TELEGRAM_CHAT_ID=TELEGRAM_CHAT_ID:latest,\
KEY_SENDERS=KEY_SENDERS:latest,\
EXCLUDED_TOPICS=EXCLUDED_TOPICS:latest,\
LOOKBACK_HOURS=LOOKBACK_HOURS:latest,\
NOTIFY_CHANNELS=NOTIFY_CHANNELS:latest,\
MODEL=MODEL:latest"

echo "--- Creating Cloud Scheduler trigger (8am and 8pm IST = 2:30 and 14:30 UTC) ---"
gcloud scheduler jobs describe "gmail-filer-schedule" --location "$REGION" --project "$PROJECT_ID" &>/dev/null \
  && gcloud scheduler jobs delete "gmail-filer-schedule" --location "$REGION" --project "$PROJECT_ID" --quiet

gcloud scheduler jobs create http "gmail-filer-schedule" \
  --location "$REGION" \
  --project "$PROJECT_ID" \
  --schedule "30 2,14 * * *" \
  --uri "https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB_NAME}:run" \
  --http-method POST \
  --oauth-service-account-email "$SA_EMAIL"

echo "--- Done. Test with: gcloud run jobs execute $JOB_NAME --region $REGION --project $PROJECT_ID ---"
