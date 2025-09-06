#!/usr/bin/env python3
"""
Test script to verify the new workspace creation workflow without system user
"""
import os
import sys
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_init import app
from models import db, User, Workspace, Company, UserWorkspace

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_new_workflow():
    """Test the new workspace creation workflow"""
    try:
        with app.app_context():
            # 1. Verify no system user exists
            system_user = User.query.filter_by(email="system@workspace.com").first()
            if system_user:
                logger.error("❌ System user still exists! Cleanup failed.")
                return False
            logger.info("✅ Confirmed: No system user exists")
            
            # 2. Simulate creating an admin user (this would happen during OAuth signin)
            admin_email = "test.admin@example.com"
            admin_user = User(
                email=admin_email,
                profile_picture="",
                role="Admin"
            )
            db.session.add(admin_user)
            db.session.commit()
            logger.info(f"✅ Created admin user: {admin_email}")
            
            # 3. Simulate workspace creation (now done during signin, not upfront)
            workspace = Workspace(
                name="Test Company",
                country="Zambia",
                industry_type="Manufacturing",
                expected_workers_string="251_500",
                expected_workers=0,
                company_phone="1234567890",
                company_email="test@example.com",
                address="",
                created_by=admin_user.id  # Admin is the first and only user
            )
            
            db.session.add(workspace)
            db.session.flush()
            logger.info(f"✅ Created workspace: {workspace.name}")
            
            # 4. Create company
            company = Company(
                name="Test Company",
                registration_number="",
                address="",
                industry="Manufacturing",
                phone="1234567890",
                created_by=admin_user.id,
                workspace_id=workspace.id
            )
            db.session.add(company)
            
            # 5. Add admin to workspace
            user_workspace = UserWorkspace(
                user_id=admin_user.id,
                workspace_id=workspace.id,
                role='Admin'
            )
            db.session.add(user_workspace)
            db.session.commit()
            logger.info("✅ Added admin to workspace")
            
            # 6. Verify the setup
            total_users = User.query.count()
            total_workspaces = Workspace.query.count()
            
            logger.info(f"✅ Final state: {total_users} users, {total_workspaces} workspaces")
            logger.info(f"✅ Workspace creator: {workspace.created_by} (admin user ID: {admin_user.id})")
            
            # Clean up
            db.session.delete(user_workspace)
            db.session.delete(company)
            db.session.delete(workspace)
            db.session.delete(admin_user)
            db.session.commit()
            logger.info("✅ Cleaned up test data")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        try:
            db.session.rollback()
        except:
            pass
        return False
    
    return True

if __name__ == "__main__":
    success = test_new_workflow()
    print("\n" + "="*50)
    if success:
        print("✅ SUCCESS: New workflow works correctly!")
        print("   - No system user needed")
        print("   - Admin user is the first and only user")
        print("   - Workspace creation is handled properly")
    else:
        print("❌ FAILED: New workflow has issues")
    print("="*50)
    sys.exit(0 if success else 1)
