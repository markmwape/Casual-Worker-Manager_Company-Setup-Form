#!/bin/bash

# Script to set up IAM permissions for accessing Google Secret Manager
set -e

echo "🔐 Setting up IAM permissions for Google Secret Manager..."

# Get current project
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No Google Cloud project set. Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "✅ Using Google Cloud project: $PROJECT_ID"

# Get the Compute Engine default service account
COMPUTE_SA="${PROJECT_ID}-compute@developer.gserviceaccount.com"

echo "🔧 Setting up permissions for service account: $COMPUTE_SA"

# Grant Secret Manager Secret Accessor role to the Compute Engine service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/secretmanager.secretAccessor"

# Also grant for Cloud Run service account (if different)
CLOUD_RUN_SA=$(gcloud iam service-accounts list --filter="email:*-compute@developer.gserviceaccount.com" --format="value(email)" | head -1)

if [ -n "$CLOUD_RUN_SA" ] && [ "$CLOUD_RUN_SA" != "$COMPUTE_SA" ]; then
    echo "🔧 Also setting up permissions for Cloud Run service account: $CLOUD_RUN_SA"
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$CLOUD_RUN_SA" \
        --role="roles/secretmanager.secretAccessor"
fi

echo "✅ IAM permissions configured successfully!"
echo ""
echo "📝 Service accounts now have access to Secret Manager:"
echo "   - $COMPUTE_SA"
if [ -n "$CLOUD_RUN_SA" ] && [ "$CLOUD_RUN_SA" != "$COMPUTE_SA" ]; then
    echo "   - $CLOUD_RUN_SA"
fi
echo ""
echo "🔍 You can verify permissions with:"
echo "gcloud projects get-iam-policy $PROJECT_ID --flatten=\"bindings[].members\" --filter=\"bindings.role:roles/secretmanager.secretAccessor\""
