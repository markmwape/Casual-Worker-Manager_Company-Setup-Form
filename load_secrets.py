import os
import logging
from google.cloud import secretmanager

def load_secrets_from_gcp():
    """Load secrets from Google Cloud Secret Manager"""
    try:
        client = secretmanager.SecretManagerServiceClient()
        
        # Try multiple ways to get project ID
        project_id = (
            os.environ.get('GOOGLE_CLOUD_PROJECT') or 
            os.environ.get('GCLOUD_PROJECT') or 
            os.environ.get('GCP_PROJECT') or
            'embee-accounting101'  # fallback
        )
        
        logging.info(f"Loading secrets from project: {project_id}")
        
        # Secret name mappings from your Google Secrets to environment variable names
        secret_mappings = {
            'stripe-pub-secret': 'STRIPE_PUBLISHABLE_KEY',
            'stripe-secret': 'STRIPE_SECRET_KEY',
            'stripe-webhook-secret': 'STRIPE_WEBHOOK_SECRET',
            'db-pass': 'DB_PASS'
        }
        
        for secret_name, env_var_name in secret_mappings.items():
            try:
                # Don't override if environment variable is already set
                if os.environ.get(env_var_name):
                    logging.info(f"Environment variable {env_var_name} already set, skipping secret {secret_name}")
                    continue
                    
                # Build the resource name of the secret version
                name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
                
                # Access the secret version
                response = client.access_secret_version(request={"name": name})
                secret_value = response.payload.data.decode("UTF-8")
                
                # Set the environment variable
                os.environ[env_var_name] = secret_value
                logging.info(f"Successfully loaded secret {secret_name} into {env_var_name}")
                
            except Exception as e:
                logging.warning(f"Failed to load secret {secret_name}: {str(e)}")
                continue
                
    except Exception as e:
        logging.warning(f"Failed to initialize Google Secret Manager client: {str(e)}")
        logging.info("Falling back to environment variables")

def ensure_secrets_loaded():
    """Ensure secrets are loaded from either Google Secret Manager or environment variables"""
    # Try to load from Google Secret Manager first (for production)
    if os.environ.get('GOOGLE_CLOUD_PROJECT') or os.environ.get('GAE_ENV'):
        load_secrets_from_gcp()
    
    # Verify required secrets are available
    required_secrets = {
        'STRIPE_SECRET_KEY': 'Stripe Secret Key',
        'STRIPE_PUBLISHABLE_KEY': 'Stripe Publishable Key', 
        'STRIPE_WEBHOOK_SECRET': 'Stripe Webhook Secret'
    }
    
    missing_secrets = []
    for env_var, description in required_secrets.items():
        if not os.environ.get(env_var):
            missing_secrets.append(f"{env_var} ({description})")
    
    if missing_secrets:
        logging.warning(f"Missing required secrets: {', '.join(missing_secrets)}")
        logging.warning("Stripe integration may not work properly")
    else:
        logging.info("All required Stripe secrets are loaded")