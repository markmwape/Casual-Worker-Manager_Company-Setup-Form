#!/usr/bin/env python3
"""
Test script to verify Stripe integration is working correctly
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test that all required environment variables are set"""
    print("🔍 Testing environment variables...")
    
    required_vars = [
        'stripe-pub-secret',
        'stripe-secret',
        'stripe-webhook-secret'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"  ✅ {var}: {'*' * 10}...{os.getenv(var)[-4:]}")
    
    if missing_vars:
        print(f"  ❌ Missing variables: {', '.join(missing_vars)}")
        return False
    
    print("  ✅ All environment variables are set")
    return True

def test_tier_configuration():
    """Test that tier configuration is properly set up"""
    print("\n🔍 Testing tier configuration...")
    
    try:
        from tier_config import TIER_SPECS, STRIPE_PRICE_MAPPING, get_tier_from_price_id, validate_tier_access
        
        # Test tier specs
        print(f"  ✅ Found {len(TIER_SPECS)} tiers: {list(TIER_SPECS.keys())}")
        
        # Test price mapping
        print(f"  ✅ Found {len(STRIPE_PRICE_MAPPING)} price mappings")
        
        # Test tier pricing
        for tier, specs in TIER_SPECS.items():
            print(f"    - {tier}: ${specs['price_monthly_usd']}/month, {specs['worker_limit']} workers")
        
        # Test helper functions
        test_price_id = list(STRIPE_PRICE_MAPPING.keys())[0] if STRIPE_PRICE_MAPPING else 'price_test'
        tier = get_tier_from_price_id(test_price_id)
        print(f"  ✅ Tier lookup function working: {test_price_id} -> {tier}")
        
        return True
    except ImportError as e:
        print(f"  ❌ Could not import tier configuration: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error testing tier configuration: {e}")
        return False

def test_stripe_connection():
    """Test connection to Stripe API"""
    print("\n🔍 Testing Stripe API connection...")
    
    try:
        import stripe
        stripe.api_key = os.getenv('stripe-secret')
        
        # Test API connection
        account = stripe.Account.retrieve()
        print(f"  ✅ Connected to Stripe account: {account.id}")
        
        # List products
        products = stripe.Product.list(limit=5)
        print(f"  ✅ Found {len(products.data)} products in Stripe")
        
        # List prices
        prices = stripe.Price.list(limit=5)
        print(f"  ✅ Found {len(prices.data)} prices in Stripe")
        
        return True
    except Exception as e:
        print(f"  ❌ Stripe API connection failed: {e}")
        return False

def test_subscription_middleware():
    """Test that subscription middleware is properly configured"""
    print("\n🔍 Testing subscription middleware...")
    
    try:
        from subscription_middleware import subscription_required, feature_required, worker_limit_check
        
        print("  ✅ Imported subscription decorators successfully")
        
        # Test that decorators are callable
        if callable(subscription_required) and callable(feature_required) and callable(worker_limit_check):
            print("  ✅ All decorators are callable")
            return True
        else:
            print("  ❌ Some decorators are not callable")
            return False
            
    except ImportError as e:
        print(f"  ❌ Could not import subscription middleware: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error testing subscription middleware: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Stripe Integration Setup")
    print("=" * 50)
    
    tests = [
        test_environment_variables,
        test_tier_configuration,
        test_stripe_connection,
        test_subscription_middleware
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Stripe integration is ready.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
