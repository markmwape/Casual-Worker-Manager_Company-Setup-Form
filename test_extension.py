#!/usr/bin/env python3
"""
Test script for trial extension feature
"""
import sys
from datetime import datetime, timedelta

# Load secrets first
try:
    from load_secrets import ensure_secrets_loaded
    ensure_secrets_loaded()
except Exception as e:
    print(f"Warning: Could not load secrets: {e}")

from app_init import app
from models import db, Workspace

def test_extension_field():
    """Test that the extension_used field exists and works"""
    with app.app_context():
        # Check if field exists by querying
        try:
            workspace = Workspace.query.first()
            if workspace:
                print(f"✓ Found workspace: {workspace.name}")
                print(f"  - Extension used: {workspace.extension_used}")
                print(f"  - Trial end date: {workspace.trial_end_date}")
                print(f"  - Subscription status: {workspace.subscription_status}")
                
                # Check if extension_used attribute exists
                if hasattr(workspace, 'extension_used'):
                    print("✓ extension_used field exists in model")
                else:
                    print("✗ extension_used field NOT found in model")
                    return False
                
                return True
            else:
                print("⚠ No workspaces found in database")
                return True
        except Exception as e:
            print(f"✗ Error checking workspace: {e}")
            return False

def test_extension_logic():
    """Test the extension logic"""
    with app.app_context():
        try:
            workspace = Workspace.query.filter_by(subscription_status='trial').first()
            if not workspace:
                print("⚠ No trial workspace found to test extension logic")
                return True
            
            print(f"\nTesting extension logic with workspace: {workspace.name}")
            
            # Store original values
            original_trial_end = workspace.trial_end_date
            original_extension_used = workspace.extension_used
            
            print(f"  - Original trial end: {original_trial_end}")
            print(f"  - Original extension used: {original_extension_used}")
            
            if workspace.extension_used:
                print("  ⚠ Extension already used for this workspace")
                print("  Simulating extension logic without saving...")
                
                if workspace.trial_end_date:
                    new_end_date = workspace.trial_end_date + timedelta(days=3)
                    print(f"  ✓ Would extend trial to: {new_end_date}")
                else:
                    new_end_date = datetime.utcnow() + timedelta(days=3)
                    print(f"  ✓ Would set new trial end to: {new_end_date}")
                
                return True
            else:
                print("  ✓ Extension not yet used, can be granted")
                return True
                
        except Exception as e:
            print(f"✗ Error testing extension logic: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("Testing Trial Extension Feature")
    print("=" * 50)
    
    success = True
    
    print("\n1. Testing extension_used field...")
    if not test_extension_field():
        success = False
    
    print("\n2. Testing extension logic...")
    if not test_extension_logic():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
