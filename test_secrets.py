#!/usr/bin/env python3
"""
Test script to verify secrets are loading correctly from Google Secret Manager
"""
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_secret_loading():
    """Test that secrets are loading correctly"""
    print("🔐 Testing Secret Loading from Google Secret Manager")
    print("=" * 60)
    
    # Load secrets
    try:
        from load_secrets import ensure_secrets_loaded
        ensure_secrets_loaded()
        print("✅ Secret loading function executed successfully")
    except Exception as e:
        print(f"❌ Error loading secrets: {e}")
        return False
    
    # Check required environment variables
    required_secrets = {
        'STRIPE_SECRET_KEY': 'Stripe Secret Key',
        'STRIPE_PUBLISHABLE_KEY': 'Stripe Publishable Key',
        'STRIPE_WEBHOOK_SECRET': 'Stripe Webhook Secret',
        'DB_PASS': 'Database Password'
    }
    
    print("\n🔍 Checking loaded secrets:")
    all_loaded = True
    
    for env_var, description in required_secrets.items():
        value = os.environ.get(env_var)
        if value:
            # Show first 4 and last 4 characters for security
            masked_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            print(f"  ✅ {env_var} ({description}): {masked_value}")
        else:
            print(f"  ❌ {env_var} ({description}): Not found")
            all_loaded = False
    
    print("\n" + "=" * 60)
    if all_loaded:
        print("🎉 All secrets loaded successfully!")
        return True
    else:
        print("❌ Some secrets are missing. Please check your Google Secret Manager setup.")
        print("\nExpected secret names in Google Secret Manager:")
        print("  - stripe-pub-secret (for STRIPE_PUBLISHABLE_KEY)")
        print("  - stripe-secret (for STRIPE_SECRET_KEY)")
        print("  - stripe-webhook-secret (for STRIPE_WEBHOOK_SECRET)")
        print("  - db-pass (for DB_PASS)")
        return False

def test_stripe_connection():
    """Test Stripe connection with loaded secrets"""
    print("\n🔌 Testing Stripe Connection")
    print("=" * 40)
    
    try:
        import stripe
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        
        if not stripe.api_key:
            print("❌ No Stripe secret key available")
            return False
        
        # Test API connection
        account = stripe.Account.retrieve()
        print(f"✅ Connected to Stripe account: {account.id}")
        print(f"✅ Account country: {account.country}")
        print(f"✅ Account email: {account.email}")
        return True
        
    except Exception as e:
        print(f"❌ Stripe connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_secret_loading()
    if success:
        test_stripe_connection()
    
    print(f"\n🏁 Test completed: {'SUCCESS' if success else 'FAILED'}")
