#!/bin/bash

# Deployment script for Google Cloud Run"
set -e

echo "🚀 Starting deployment to Google Cloud Run..."

# Set your project ID (replace with your actual project ID)
PROJECT_ID="embee-accounting101"
SERVICE_NAME="cw-manager-service"
REGION="us-central1"

# Cloud SQL Configuration (matching app.yaml and cloudbuild.yaml)
INSTANCE_CONNECTION_NAME="embee-accounting101:us-central1:cw-manager-db"
DB_USER="cwuser"
DB_NAME="cw_manager"
# DB_PASS is loaded from Google Secret Manager (secret: db-pass)

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
  --set-env-vars="INSTANCE_CONNECTION_NAME=$INSTANCE_CONNECTION_NAME,DB_USER=$DB_USER,DB_NAME=$DB_NAME,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --update-secrets="DB_PASS=db-pass:latest" \
  --add-cloudsql-instances=$INSTANCE_CONNECTION_NAME

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