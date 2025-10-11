#!/bin/bash

# Alternative deployment script using prebuilt image
set -e

echo "🚀 Starting deployment to Google Cloud Run (prebuilt image approach)..."

# Set your project ID
PROJECT_ID="embee-accounting101"
SERVICE_NAME="cw-manager-service"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Cloud SQL Configuration (matching the error logs)
CLOUD_SQL_CONNECTION_NAME="embee-accounting101:us-central1:cw-manager-db"
DB_USER="cwuser"
# DB_PASS is loaded from Google Secret Manager (secret: db-pass)
DB_NAME="cw_manager"

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
  --set-env-vars="INSTANCE_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-env-vars="DB_USER=$DB_USER" \
  --set-env-vars="DB_NAME=$DB_NAME" \
  --update-secrets="DB_PASS=db-pass:latest" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
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
