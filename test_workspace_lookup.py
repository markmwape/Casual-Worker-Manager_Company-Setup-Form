#!/usr/bin/env python3
"""
Test script to verify workspace code lookup
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_workspace_lookup():
    """Test workspace lookup by code"""
    try:
        # Import Flask app context
        from app_init import app, db
        from models import Workspace
        
        with app.app_context():
            workspace_code = "ODUNVCOV2ON8JZFU"  # From your checkout session
            
            print(f"🔍 Looking up workspace with code: {workspace_code}")
            
            # Try to find workspace by code
            workspace = Workspace.query.filter_by(workspace_code=workspace_code).first()
            
            if workspace:
                print(f"✅ Found workspace:")
                print(f"   - ID: {workspace.id}")
                print(f"   - Name: {workspace.name}")
                print(f"   - Code: {workspace.workspace_code}")
                print(f"   - Stripe Customer ID: {workspace.stripe_customer_id}")
                print(f"   - Subscription Status: {workspace.subscription_status}")
                print(f"   - Subscription Tier: {workspace.subscription_tier}")
                return True
            else:
                print(f"❌ No workspace found with code: {workspace_code}")
                
                # List all workspaces for debugging
                all_workspaces = Workspace.query.limit(10).all()
                print(f"\n📋 Available workspaces (showing first 10):")
                for ws in all_workspaces:
                    print(f"   - {ws.workspace_code}: {ws.name}")
                    
                return False
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_customer_lookup():
    """Test customer lookup"""
    try:
        from app_init import app, db
        from models import Workspace
        
        with app.app_context():
            customer_id = "cus_T1Sh8rtQQ9rEIK"  # From your checkout session
            
            print(f"\n🔍 Looking up workspace with customer ID: {customer_id}")
            
            workspace = Workspace.query.filter_by(stripe_customer_id=customer_id).first()
            
            if workspace:
                print(f"✅ Found workspace linked to customer:")
                print(f"   - ID: {workspace.id}")
                print(f"   - Name: {workspace.name}")
                print(f"   - Code: {workspace.workspace_code}")
                return True
            else:
                print(f"❌ No workspace found for customer: {customer_id}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Run workspace lookup tests"""
    print("🚀 Testing Workspace Lookup")
    print("=" * 40)
    
    success1 = test_workspace_lookup()
    success2 = test_customer_lookup()
    
    print("\n" + "=" * 40)
    if success1 or success2:
        print("✅ Workspace lookup is working!")
    else:
        print("❌ Workspace not found. Check if workspace code exists in database.")

if __name__ == "__main__":
    main()
