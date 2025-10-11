#!/bin/bash

# Deployment script for Google Cloud Run
set -e

echo "🚀 Starting deployment to Google Cloud Run..."

# Set your project ID (replace with your actual project ID)
PROJECT_ID="embee-accounting101"
SERVICE_NAME="cw-manager-service"
REGION="us-central1"

# Cloud SQL Configuration (use Google Secret Manager for production)
CLOUD_SQL_CONNECTION_NAME="embee-accounting101:us-central1:cw-manager-db"
DB_USER="cwuser"
# Note: DB_PASS should be loaded from Secret Manager in production
# For manual deployment, you need to set these environment variables:
if [[ -z "$DB_PASS" ]]; then
  echo "❌ Error: DB_PASS environment variable not set"
  echo "   Please set it with: export DB_PASS='your-password'"
  exit 1
fi
if [[ -z "$STRIPE_SECRET" ]]; then
  echo "❌ Error: STRIPE_SECRET environment variable not set"
  echo "   Please set it with: export STRIPE_SECRET='your-stripe-secret'"
  exit 1
fi
if [[ -z "$STRIPE_PUB_SECRET" ]]; then
  echo "❌ Error: STRIPE_PUB_SECRET environment variable not set"
  echo "   Please set it with: export STRIPE_PUB_SECRET='your-stripe-publishable-key'"
  exit 1
fi
if [[ -z "$STRIPE_WEBHOOK_SECRET" ]]; then
  echo "❌ Error: STRIPE_WEBHOOK_SECRET environment variable not set"
  echo "   Please set it with: export STRIPE_WEBHOOK_SECRET='your-stripe-webhook-secret'"
  exit 1
fi
DB_NAME="cw_manager"

echo "📦 Building and deploying to Cloud Run..."

# Build and deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 1 \
  --timeout 300 \
  --concurrency 80 \
  --max-instances 10 \
  --min-instances 0 \
  --port 8080 \
  --set-env-vars="INSTANCE_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-env-vars="DB_USER=$DB_USER" \
  --set-env-vars="DB_PASS=$DB_PASS" \
  --set-env-vars="DB_NAME=$DB_NAME" \
  --set-env-vars="stripe-secret=$STRIPE_SECRET" \
  --set-env-vars="stripe-pub-secret=$STRIPE_PUB_SECRET" \
  --set-env-vars="stripe-webhook-secret=$STRIPE_WEBHOOK_SECRET" \
  --add-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME

echo "✅ Deployment completed!"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "🌐 Your app is available at: $SERVICE_URL"

echo ""
echo "🔄 Running database migrations..."
echo "This will create the database schema on your Cloud SQL instance."

# Run migrations by making a request to the health endpoint which triggers migrations
curl -s "$SERVICE_URL/health" > /dev/null
echo "✅ Migrations completed!"

echo ""
echo "📊 To view logs:"
echo "gcloud logs tail --service=$SERVICE_NAME --region=$REGION"

echo ""
echo "🔧 To check health:"
echo "curl $SERVICE_URL/health" 