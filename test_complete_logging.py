#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, Workspace, User, Company, UserWorkspace
from app_init import app
from activity_logger import log_activity, LogMessages

def create_demo_data():
    """Create demo workspace and user for testing"""
    with app.app_context():
        try:
            # Check if demo data already exists
            demo_user = User.query.filter_by(email='demo@example.com').first()
            if demo_user:
                print("✓ Demo data already exists")
                return demo_user
            
            # Create demo user
            demo_user = User(email='demo@example.com')
            db.session.add(demo_user)
            db.session.flush()
            
            # Create demo workspace
            demo_workspace = Workspace(
                name='Demo Workspace',
                country='United States',
                industry_type='Technology',
                expected_workers_string='1-10',
                company_phone='+1234567890',
                company_email='demo@example.com',
                address='123 Demo Street',
                created_by=demo_user.id
            )
            db.session.add(demo_workspace)
            db.session.flush()
            
            # Create demo company
            demo_company = Company(
                name='Demo Company',
                registration_number='DEMO123',
                address='123 Demo Street',
                industry='Technology',
                phone='+1234567890',
                created_by=demo_user.id,
                workspace_id=demo_workspace.id
            )
            db.session.add(demo_company)
            
            # Add user to workspace
            user_workspace = UserWorkspace(
                user_id=demo_user.id,
                workspace_id=demo_workspace.id,
                role='Admin'
            )
            db.session.add(user_workspace)
            
            db.session.commit()
            
            print("✅ Demo data created successfully!")
            print(f"  - User: {demo_user.email}")
            print(f"  - Workspace: {demo_workspace.name}")
            print(f"  - Company: {demo_company.name}")
            
            return demo_user
            
        except Exception as e:
            print(f"❌ Error creating demo data: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return None

def test_activity_logging_with_demo():
    """Test the activity logging functionality with demo data"""
    with app.app_context():
        try:
            # Create demo data
            demo_user = create_demo_data()
            if not demo_user:
                return
            
            demo_workspace = Workspace.query.filter_by(name='Demo Workspace').first()
            
            # Test various activity log types
            test_activities = [
                {
                    'action_type': 'create',
                    'resource_type': 'worker',
                    'description': LogMessages.WORKER_CREATED.format(name='John Doe'),
                    'details': {'worker_name': 'John Doe', 'company_id': 1}
                },
                {
                    'action_type': 'create', 
                    'resource_type': 'task',
                    'description': LogMessages.TASK_CREATED.format(name='Demo Task'),
                    'details': {'task_name': 'Demo Task', 'payment_type': 'per_day'}
                },
                {
                    'action_type': 'update',
                    'resource_type': 'company',
                    'description': LogMessages.COMPANY_PAYOUT_UPDATED.format(currency='$', amount=50.0),
                    'details': {'old_rate': 40.0, 'new_rate': 50.0}
                },
                {
                    'action_type': 'login',
                    'resource_type': 'workspace',
                    'description': LogMessages.USER_LOGIN,
                    'details': {'workspace_name': demo_workspace.name}
                }
            ]
            
            # Create test logs
            for activity in test_activities:
                log_activity(
                    action_type=activity['action_type'],
                    resource_type=activity['resource_type'],
                    description=activity['description'],
                    details=activity['details'],
                    user_email=demo_user.email,
                    workspace_id=demo_workspace.id
                )
            
            # Query and display logs
            from activity_logger import get_recent_activities, get_activity_stats
            
            recent_activities = get_recent_activities(demo_workspace.id, limit=10)
            activity_stats = get_activity_stats(demo_workspace.id, days=7)
            
            print(f"\n✅ Created {len(test_activities)} test activity logs")
            print(f"✅ Retrieved {len(recent_activities)} recent activities")
            print(f"✅ Activity stats: {activity_stats['total_activities']} total activities")
            
            print("\n📋 Recent Activities:")
            for activity in recent_activities:
                print(f"  - {activity['action_type'].upper()}: {activity['description']}")
                print(f"    User: {activity['user_email']} | Time: {activity.get('time_ago', 'Unknown')}")
            
            print("\n📊 Activity Statistics:")
            for action_type, count in activity_stats['activity_counts'].items():
                print(f"  - {action_type.title()}: {count}")
            
            print("\n✅ Activity logging system is fully functional!")
            
        except Exception as e:
            print(f"❌ Error testing activity logging: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_activity_logging_with_demo()
