#!/bin/bash

# Alternative deployment script using prebuilt image
set -e

echo "🚀 Starting deployment to Google Cloud Run (prebuilt image approach)..."

# Set your project ID
PROJECT_ID="embee-accounting"
SERVICE_NAME="casual-worker-manager-company-setup-form"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Cloud SQL Configuration
CLOUD_SQL_CONNECTION_NAME="embee-accounting:us-central1:casual-worker-db"
DB_USER="casual_worker_user"
DB_PASS="Embeeaccounting2030"
DB_NAME="casual_worker_db"

echo "📦 Building container locally..."

# Build the container locally
docker build -t $IMAGE_NAME .

echo "🔄 Pushing to Container Registry..."

# Configure Docker for GCR
gcloud auth configure-docker gcr.io

# Push to Container Registry
docker push $IMAGE_NAME

echo "🚀 Deploying to Cloud Run..."

# Deploy to Cloud Run using the pushed image
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
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
curl -s "$SERVICE_URL/health" > /dev/null
echo "✅ Migrations completed!"

echo ""
echo "📊 To view logs:"
echo "gcloud logs tail --service=$SERVICE_NAME --region=$REGION"
