#!/bin/bash

# Simple deployment script for Casual Worker Manager
# This script triggers a Cloud Build deployment

echo "🚀 Starting deployment of Casual Worker Manager..."

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Please authenticate with gcloud first:"
    echo "   gcloud auth login"
    exit 1
fi

# Get current project
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No project set. Please set your project:"
    echo "   gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📊 Deploying to project: $PROJECT_ID"

# Trigger Cloud Build
echo "🔧 Triggering Cloud Build..."
gcloud builds submit --config cloudbuild.yaml .

if [ $? -eq 0 ]; then
    echo "✅ Deployment completed successfully!"
    echo "🌐 Your application should be available at:"
    echo "   https://cw-manager-service-[hash]-uc.a.run.app"
    echo ""
    echo "💡 To get the exact URL, run:"
    echo "   gcloud run services describe cw-manager-service --region=us-central1 --format='value(status.url)'"
else
    echo "❌ Deployment failed!"
    exit 1
fi
