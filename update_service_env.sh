#!/bin/bash

# Update the Cloud Run service with correct environment variables
echo "Updating Cloud Run service with environment variables..."

gcloud run services update embee-accounting \
  --region=us-central1 \
  --set-env-vars="INSTANCE_CONNECTION_NAME=embee-accounting101:us-central1:cw-manager-db,DB_USER=cwuser,DB_PASS=CWManager2024!,DB_NAME=cw_manager" \
  --add-cloudsql-instances=embee-accounting101:us-central1:cw-manager-db \
  --quiet

echo "Service updated successfully!"

# Check the service configuration
echo "Current service configuration:"
gcloud run services describe embee-accounting --region=us-central1
