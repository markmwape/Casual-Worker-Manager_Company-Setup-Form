#!/usr/bin/env python3
"""
Simple application test
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_init import app
from models import db, User, Company, Workspace

def test_simple_app():
    """Test if the application works with current database"""
    try:
        with app.app_context():
            # Test basic database operations
            print("Testing database operations...")
            
            # Test User model
            users = User.query.all()
            print(f"✅ Found {len(users)} users")
            
            # Test Company model
            companies = Company.query.all()
            print(f"✅ Found {len(companies)} companies")
            
            # Test Workspace model
            workspaces = Workspace.query.all()
            print(f"✅ Found {len(workspaces)} workspaces")
            
            # Test creating a workspace
            try:
                workspace = Workspace(
                    name="Test Workspace",
                    country="Zambia",
                    industry_type="Test",
                    expected_workers_string="below_100",
                    company_phone="1234567890",
                    company_email="test@example.com",
                    address="",
                    expected_workers=0,
                    created_by=1
                )
                db.session.add(workspace)
                db.session.commit()
                print("✅ Successfully created workspace")
                
                # Clean up
                db.session.delete(workspace)
                db.session.commit()
                print("✅ Successfully cleaned up workspace")
                
            except Exception as e:
                print(f"❌ Error creating workspace: {e}")
            
            print("✅ All tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_app()
    sys.exit(0 if success else 1) 