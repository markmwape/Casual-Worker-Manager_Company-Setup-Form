# Secret Management Setup

This document explains how database passwords and API keys are securely managed using Google Cloud Secret Manager instead of being hardcoded in the application.

## Overview

All sensitive credentials are now stored in Google Cloud Secret Manager and loaded at runtime. This includes:

- Database passwords
- Stripe API keys
- Stripe webhook secrets

## Secret Mappings

The following secrets should be created in Google Cloud Secret Manager:

| Secret Name in GCP | Environment Variable | Description |
|-------------------|---------------------|-------------|
| `stripe-pub-secret` | `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key (pk_...) |
| `stripe-secret` | `STRIPE_SECRET_KEY` | Stripe secret key (sk_...) |
| `stripe-webhook-secret` | `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret (whsec_...) |
| `db-pass` | `DB_PASS` | Database password |

## Setup Instructions

### 1. Create Secrets in Google Secret Manager

```bash
# Create each secret (replace SECRET_VALUE with actual values)
echo 'pk_test_your_publishable_key' | gcloud secrets create stripe-pub-secret --data-file=-
echo 'sk_test_your_secret_key' | gcloud secrets create stripe-secret --data-file=-
echo 'whsec_your_webhook_secret' | gcloud secrets create stripe-webhook-secret --data-file=-
echo 'your_database_password' | gcloud secrets create db-pass --data-file=-
```

### 2. Set Up IAM Permissions

```bash
# Run the setup script to configure IAM permissions
./setup_secret_permissions.sh
```

### 3. Verify Setup

```bash
# Verify secrets are properly configured
python3 verify_secrets.py

# Test secret loading
python3 test_secrets.py
```

### 4. Deploy with Secrets

```bash
# Use the secure deployment script
./deploy_with_secrets.sh
```

## How It Works

1. **At Startup**: The `load_secrets.py` module loads secrets from Google Secret Manager into environment variables
2. **In Production**: Cloud Run service account has `roles/secretmanager.secretAccessor` permission
3. **Fallback**: If Secret Manager is unavailable, the app falls back to existing environment variables

## Security Benefits

- ✅ No hardcoded passwords in source code
- ✅ Passwords are encrypted at rest in Google Secret Manager
- ✅ Access is controlled via IAM permissions
- ✅ Audit trail of secret access
- ✅ Easy secret rotation without code changes

## Files Modified

The following files were updated to remove hardcoded passwords:

- `deploy_prebuilt.sh` - Removed hardcoded DB_PASS
- `deploy.sh` - Removed hardcoded DB_PASS  
- `app.yaml` - Removed hardcoded DB_PASS
- `cloudbuild.yaml` - Removed hardcoded DB_PASS
- `update_service_env.sh` - Removed hardcoded DB_PASS
- `.github/workflows/deploy.yml` - Removed hardcoded DB_PASS

## Troubleshooting

### Secret Loading Issues

If secrets fail to load:

1. Check IAM permissions: `./setup_secret_permissions.sh`
2. Verify secrets exist: `python3 verify_secrets.py`
3. Check Cloud Run logs for secret loading errors

### Deployment Issues

If deployment fails:

1. Ensure all required secrets are created in Secret Manager
2. Verify IAM permissions are set correctly
3. Check that the correct project ID is being used

### Testing Locally

For local development, you can still use environment variables:

```bash
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_PUBLISHABLE_KEY="pk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
export DB_PASS="your_local_password"
```

The secret loading system will not override existing environment variables.
