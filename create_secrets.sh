#!/bin/bash

# Interactive script to create all required secrets in Google Secret Manager
set -e

echo "🔐 Google Secret Manager Setup"
echo "=============================="
echo ""

# Check authentication
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1 > /dev/null; then
    echo "❌ Please authenticate with Google Cloud first:"
    echo "gcloud auth login"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No Google Cloud project set. Please run:"
    echo "gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "✅ Using project: $PROJECT_ID"
echo ""

# Function to create or update a secret
create_secret() {
    local secret_name=$1
    local description=$2
    local example=$3
    
    echo "🔑 Setting up: $secret_name"
    echo "   Description: $description"
    echo "   Example format: $example"
    echo ""
    
    # Check if secret already exists
    if gcloud secrets describe "$secret_name" --project="$PROJECT_ID" >/dev/null 2>&1; then
        echo "   Secret '$secret_name' already exists."
        read -p "   Do you want to update it? (y/N): " update_secret
        if [[ $update_secret =~ ^[Yy]$ ]]; then
            read -s -p "   Enter new value for $secret_name: " secret_value
            echo ""
            echo "$secret_value" | gcloud secrets versions add "$secret_name" --data-file=-
            echo "   ✅ Secret updated"
        else
            echo "   ⏭️  Skipping"
        fi
    else
        read -s -p "   Enter value for $secret_name: " secret_value
        echo ""
        if [ -n "$secret_value" ]; then
            echo "$secret_value" | gcloud secrets create "$secret_name" --data-file=-
            echo "   ✅ Secret created"
        else
            echo "   ⏭️  Skipping (empty value)"
        fi
    fi
    echo ""
}

# Create each secret
create_secret "stripe-pub-secret" "Stripe Publishable Key" "pk_test_..."
create_secret "stripe-secret" "Stripe Secret Key" "sk_test_..."
create_secret "stripe-webhook-secret" "Stripe Webhook Secret" "whsec_..."
create_secret "db-pass" "Database Password" "your-secure-password"

echo "🎉 Secret setup completed!"
echo ""
echo "Next steps:"
echo "1. Set up IAM permissions: ./setup_secret_permissions.sh"
echo "2. Verify setup: python3 verify_secrets.py"
echo "3. Test secret loading: python3 test_secrets.py"
echo "4. Deploy: ./deploy_with_secrets.sh"
