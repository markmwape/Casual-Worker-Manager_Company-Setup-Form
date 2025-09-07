#!/bin/bash
# Deploy with correct environment variables for Cloud SQL

echo "Deploying Casual Worker Manager with Cloud SQL configuration..."

# Deploy to Cloud Run with proper environment variables
gcloud run deploy cw-manager-service \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --add-cloudsql-instances embee-accounting101:us-central1:cw-manager-db \
  --set-env-vars="INSTANCE_CONNECTION_NAME=embee-accounting101:us-central1:cw-manager-db" \
  --set-env-vars="DB_USER=postgres" \
  --set-env-vars="DB_NAME=cw_manager" \
  --set-env-vars="DB_PASS=temppass123" \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300

echo "Deployment complete!"
echo "Service URL:"
gcloud run services describe cw-manager-service --region=us-central1 --format="value(status.url)"
