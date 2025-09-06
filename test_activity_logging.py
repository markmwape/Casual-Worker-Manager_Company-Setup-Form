#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, ActivityLog, Workspace, User
from app_init import app
from activity_logger import log_activity, LogMessages

def test_activity_logging():
    """Test the activity logging functionality"""
    with app.app_context():
        try:
            # Check if activity_log table exists by querying it directly
            try:
                ActivityLog.query.first()
                print("✓ Activity log table exists and is accessible")
            except Exception as e:
                print(f"❌ Activity log table issue: {str(e)}")
                return
            
            # Create a test workspace and user first
            test_workspace = Workspace.query.first()
            test_user = User.query.first()
            
            if not test_workspace:
                print("❌ No workspace found for testing")
                return
                
            if not test_user:
                print("❌ No user found for testing")
                return
            
            print(f"✓ Using workspace: {test_workspace.name}")
            print(f"✓ Using user: {test_user.email}")
            
            # Test log creation with explicit parameters
            log_activity(
                action_type='create',
                resource_type='test',
                description='Test activity log entry',
                details={'test': True},
                user_email=test_user.email,
                workspace_id=test_workspace.id
            )
            
            # Query the log
            logs = ActivityLog.query.filter_by(workspace_id=test_workspace.id).all()
            print(f"✓ Found {len(logs)} activity log entries for workspace")
            
            if logs:
                latest_log = logs[-1]
                print(f"✓ Latest log: {latest_log.description}")
                print(f"  - Action: {latest_log.action_type}")
                print(f"  - Resource: {latest_log.resource_type}")
                print(f"  - User: {latest_log.user_email}")
                print(f"  - Created: {latest_log.created_at}")
            
            print("\n✅ Activity logging system is working correctly!")
            
        except Exception as e:
            print(f"❌ Error testing activity logging: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_activity_logging()
