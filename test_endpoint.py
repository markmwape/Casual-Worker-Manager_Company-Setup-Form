#!/usr/bin/env python3
"""
Quick endpoint test - Tests that the endpoint exists and responds correctly
"""
import sys

try:
    from load_secrets import ensure_secrets_loaded
    ensure_secrets_loaded()
except:
    pass

from app_init import app

def test_endpoint_exists():
    """Test that the endpoint is registered"""
    with app.app_context():
        # Get all routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))
        
        # Check if our endpoint exists
        if '/api/request-trial-extension' in routes:
            print("✓ /api/request-trial-extension endpoint is registered")
            
            # Get the endpoint details
            for rule in app.url_map.iter_rules():
                if str(rule) == '/api/request-trial-extension':
                    print(f"  Methods: {rule.methods}")
                    print(f"  Endpoint: {rule.endpoint}")
            return True
        else:
            print("✗ /api/request-trial-extension endpoint NOT found")
            print("\nAvailable API endpoints:")
            for route in sorted(routes):
                if '/api/' in route:
                    print(f"  - {route}")
            return False

if __name__ == '__main__':
    print("Testing Endpoint Registration")
    print("=" * 50)
    
    if test_endpoint_exists():
        print("\n✓ Endpoint test passed!")
        sys.exit(0)
    else:
        print("\n✗ Endpoint test failed!")
        sys.exit(1)
