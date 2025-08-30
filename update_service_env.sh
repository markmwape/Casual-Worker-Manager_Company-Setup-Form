#!/bin/bash

# Update the Cloud Run service with correct environment variables
echo "Updating Cloud Run service with environment variables..."

gcloud run services update embee-accounting \
  --region=us-central1 \
  --set-env-vars="INSTANCE_CONNECTION_NAME=embee-accounting101:us-central1:embee-accounting,DB_USER=embee-accounting,DB_PASS=EmbeeMarkSQL2024!,DB_NAME=embee-accounting" \
  --add-cloudsql-instances=embee-accounting101:us-central1:embee-accounting \
  --quiet

echo "Service updated successfully!"

# Check the service configuration
echo "Current service configuration:"
gcloud run services describe embee-accounting --region=us-central1
