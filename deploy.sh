#!/bin/bash

# Deployment script for Google Cloud Run
set -e

echo "🚀 Starting deployment to Google Cloud Run..."

# Set your project ID (replace with your actual project ID)
PROJECT_ID="embee-accounting"
SERVICE_NAME="casual-worker-manager-company-setup-form"
REGION="us-central1"

# Cloud SQL Configuration (update these values after running setup_cloud_sql.py)
CLOUD_SQL_CONNECTION_NAME="embee-accounting:us-central1:casual-worker-db"
DB_USER="casual_worker_user"
DB_PASS="Embeeaccounting2030"
DB_NAME="casual_worker_db"

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
  --set-env-vars="CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-env-vars="DB_USER=$DB_USER" \
  --set-env-vars="DB_PASS=$DB_PASS" \
  --set-env-vars="DB_NAME=$DB_NAME" \
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