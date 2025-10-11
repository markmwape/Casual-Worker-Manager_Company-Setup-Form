#!/bin/bash

# Deployment script with secret verification
set -e

echo "🚀 Preparing deployment with secret verification..."

# Check if we're in the correct directory
if [ ! -f "main.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check Google Cloud authentication
echo "🔐 Checking Google Cloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1 > /dev/null; then
    echo "❌ Not authenticated with Google Cloud. Please run: gcloud auth login"
    exit 1
fi

# Get current project
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No Google Cloud project set. Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "✅ Using Google Cloud project: $PROJECT_ID"

# Verify secrets exist in Secret Manager
echo "🔍 Verifying secrets in Google Secret Manager..."

REQUIRED_SECRETS=("stripe-pub-secret" "stripe-secret" "stripe-webhook-secret" "db-pass")
MISSING_SECRETS=()

for secret in "${REQUIRED_SECRETS[@]}"; do
    if gcloud secrets describe "$secret" --project="$PROJECT_ID" >/dev/null 2>&1; then
        echo "✅ Secret '$secret' found"
    else
        echo "❌ Secret '$secret' not found"
        MISSING_SECRETS+=("$secret")
    fi
done

if [ ${#MISSING_SECRETS[@]} -gt 0 ]; then
    echo ""
    echo "❌ Missing secrets in Google Secret Manager:"
    for secret in "${MISSING_SECRETS[@]}"; do
        echo "   - $secret"
    done
    echo ""
    echo "Please create these secrets using:"
    echo "gcloud secrets create SECRET_NAME --data-file=- <<< 'SECRET_VALUE'"
    echo ""
    echo "Expected secret mappings:"
    echo "  stripe-pub-secret     -> Your Stripe publishable key (pk_...)"
    echo "  stripe-secret         -> Your Stripe secret key (sk_...)"
    echo "  stripe-webhook-secret -> Your Stripe webhook secret (whsec_...)"
    echo "  db-pass              -> Your database password"
    exit 1
fi

# Set up IAM permissions for Secret Manager
echo "🔐 Setting up IAM permissions for Secret Manager..."
if ./setup_secret_permissions.sh; then
    echo "✅ IAM permissions configured"
else
    echo "⚠️  IAM setup failed, but continuing deployment..."
fi

# Test secret loading locally
echo "🧪 Testing secret loading..."
if python3 test_secrets.py; then
    echo "✅ Secret loading test passed"
else
    echo "❌ Secret loading test failed"
    exit 1
fi

# Build and deploy
echo "🏗️  Building and deploying to Cloud Run..."

# Use the existing deployment script
if [ -f "deploy_prebuilt.sh" ]; then
    ./deploy_prebuilt.sh
else
    echo "❌ deploy_prebuilt.sh not found"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo ""
echo "🔗 Your application should now have access to:"
echo "   - Stripe API keys from Google Secret Manager"
echo "   - Database password from Google Secret Manager"
echo "   - All webhook functionality should work properly"
