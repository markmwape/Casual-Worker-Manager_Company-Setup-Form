#!/usr/bin/env python3
"""
Test script to debug workspace creation
"""
import os
import sys
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_init import app
from models import db, User, Workspace

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_workspace_creation():
    """Test workspace creation"""
    try:
        with app.app_context():
            # Check if user with ID 1 exists
            user = User.query.get(1)
            logger.info(f"User with ID 1 exists: {user is not None}")
            if user:
                logger.info(f"User email: {user.email}")
            
            # List all users
            all_users = User.query.all()
            logger.info(f"Total users in database: {len(all_users)}")
            for u in all_users:
                logger.info(f"User ID: {u.id}, Email: {u.email}")
            
            # Try to create a workspace
            try:
                workspace = Workspace(
                    name="Test Company",
                    country="Zambia",
                    industry_type="Manufacturing",
                    expected_workers_string="251_500",
                    expected_workers=0,  # Add default value
                    company_phone="1234567890",
                    company_email="test@example.com",
                    address="",  # Add empty address
                    created_by=1
                )
                
                logger.info(f"Workspace object created: {workspace}")
                logger.info(f"Workspace data: {workspace.__dict__}")
                
                db.session.add(workspace)
                db.session.commit()
                logger.info("✓ Workspace created successfully!")
                
                # Clean up
                db.session.delete(workspace)
                db.session.commit()
                logger.info("✓ Workspace cleaned up")
                
            except Exception as e:
                logger.error(f"✗ Error creating workspace: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                db.session.rollback()
            
    except Exception as e:
        logger.error(f"✗ Test failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_workspace_creation()
    sys.exit(0 if success else 1) 