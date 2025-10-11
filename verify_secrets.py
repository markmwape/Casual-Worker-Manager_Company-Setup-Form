#!/usr/bin/env python3
"""
Quick script to verify your Google Secret Manager setup and provide guidance
"""
import subprocess
import sys

def check_secret_exists(secret_name, project_id):
    """Check if a secret exists in Google Secret Manager"""
    try:
        result = subprocess.run([
            'gcloud', 'secrets', 'describe', secret_name, 
            f'--project={project_id}'
        ], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def get_secret_value(secret_name, project_id):
    """Get the first few characters of a secret value for verification"""
    try:
        result = subprocess.run([
            'gcloud', 'secrets', 'versions', 'access', 'latest',
            f'--secret={secret_name}', f'--project={project_id}'
        ], capture_output=True, text=True)
        if result.returncode == 0:
            value = result.stdout.strip()
            return f"{value[:8]}..." if len(value) > 8 else "***"
        return None
    except Exception:
        return None

def main():
    print("🔐 Google Secret Manager Setup Verification")
    print("=" * 50)
    
    # Get project ID
    try:
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                               capture_output=True, text=True)
        project_id = result.stdout.strip()
    except Exception:
        print("❌ Could not get Google Cloud project ID")
        print("Please run: gcloud config set project YOUR_PROJECT_ID")
        return
    
    print(f"Project: {project_id}")
    print()
    
    # Check each secret
    secrets_info = {
        'stripe-pub-secret': {
            'description': 'Stripe Publishable Key',
            'expected_prefix': 'pk_',
            'maps_to': 'STRIPE_PUBLISHABLE_KEY'
        },
        'stripe-secret': {
            'description': 'Stripe Secret Key', 
            'expected_prefix': 'sk_',
            'maps_to': 'STRIPE_SECRET_KEY'
        },
        'stripe-webhook-secret': {
            'description': 'Stripe Webhook Secret',
            'expected_prefix': 'whsec_',
            'maps_to': 'STRIPE_WEBHOOK_SECRET'
        },
        'db-pass': {
            'description': 'Database Password',
            'expected_prefix': None,
            'maps_to': 'DB_PASS'
        }
    }
    
    all_good = True
    
    for secret_name, info in secrets_info.items():
        print(f"🔍 Checking {secret_name} ({info['description']})...")
        
        if check_secret_exists(secret_name, project_id):
            value_preview = get_secret_value(secret_name, project_id)
            if value_preview:
                if info['expected_prefix'] and not value_preview.startswith(info['expected_prefix']):
                    print(f"  ⚠️  Secret exists but may have wrong format")
                    print(f"     Expected to start with: {info['expected_prefix']}")
                    print(f"     Actual value starts with: {value_preview}")
                    all_good = False
                else:
                    print(f"  ✅ Secret exists: {value_preview}")
            else:
                print(f"  ❌ Could not access secret value")
                all_good = False
        else:
            print(f"  ❌ Secret does not exist")
            all_good = False
            
        print(f"     Maps to environment variable: {info['maps_to']}")
        print()
    
    if all_good:
        print("🎉 All secrets are properly configured!")
        print()
        print("Your secrets will be loaded as:")
        for secret_name, info in secrets_info.items():
            print(f"  {secret_name} → {info['maps_to']}")
    else:
        print("❌ Some secrets need attention. Please fix the issues above.")
        print()
        print("To create or update a secret:")
        print("gcloud secrets create SECRET_NAME --data-file=- <<< 'SECRET_VALUE'")
        print("# or to update:")
        print("echo 'SECRET_VALUE' | gcloud secrets versions add SECRET_NAME --data-file=-")

if __name__ == "__main__":
    main()
