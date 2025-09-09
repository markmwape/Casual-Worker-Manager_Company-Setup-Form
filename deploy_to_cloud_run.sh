#!/bin/bash

# Deploy Casual Worker Manager to Google Cloud Run
# This script builds and deploys the application with proper database initialization

set -e

echo "🚀 Deploying Casual Worker Manager to Google Cloud Run..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No project set. Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Using project: $PROJECT_ID"

# Build and deploy using Cloud Build
echo "🔨 Building and deploying with Cloud Build..."
gcloud builds submit --config cloudbuild.yaml .

echo "✅ Deployment completed!"
echo ""
echo "🌐 Your application should be available at:"
echo "https://cw-manager-service-YOUR_HASH-uc.a.run.app"
echo ""
echo "📝 To get the exact URL, run:"
echo "gcloud run services describe cw-manager-service --region=us-central1 --format='value(status.url)'"
echo ""
echo "🔍 To view logs, run:"
echo "gcloud run services logs tail cw-manager-service --region=us-central1"
