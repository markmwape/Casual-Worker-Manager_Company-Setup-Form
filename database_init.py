#!/usr/bin/env python3
"""
Database initialization script for Casual Worker Manager
This script creates all necessary database tables and initial data.
"""

import os
import logging
from datetime import datetime, timedelta

def init_database():
    """Initialize database with all required tables and initial data"""
    try:
        from app_init import app, db
        from models import (
            User, Workspace, UserWorkspace, Company, Worker, Task, 
            Attendance, MasterAdmin, ActivityLog, ImportField, 
            WorkerCustomFieldValue, WorkerImportLog, ReportField
        )
        
        with app.app_context():
            logging.info("🔧 Starting database initialization...")
            
            # Create all tables
            db.create_all()
            logging.info("✅ Database tables created successfully")
            
            # Ensure workspace table has all necessary columns (in case of existing DB schema)
            engine = db.engine
            required_workspace_columns = {
                'stripe_customer_id': 'VARCHAR(255)',
                'stripe_subscription_id': 'VARCHAR(255)',
                'subscription_status': "VARCHAR(50) DEFAULT 'trial'",
                'subscription_tier': "VARCHAR(50) DEFAULT 'basic'",
                'trial_end_date': 'TIMESTAMP',
                'subscription_end_date': 'TIMESTAMP'
            }
            with engine.connect() as conn:
                for col, col_def in required_workspace_columns.items():
                    try:
                        conn.execute(f"ALTER TABLE workspace ADD COLUMN {col} {col_def};")
                        logging.info(f"Added missing column to workspace: {col}")
                    except Exception:
                        # Column probably exists already
                        pass
            
            # Check if this is production
            is_production = os.environ.get('K_SERVICE') or os.environ.get('GAE_ENV') or os.environ.get('INSTANCE_CONNECTION_NAME')
            
            # Create master admin user if not exists
            master_admin_email = os.environ.get('MASTER_ADMIN_EMAIL', 'markbmwape@gmail.com')
            existing_admin = MasterAdmin.query.filter_by(email=master_admin_email).first()
            
            if not existing_admin:
                master_admin = MasterAdmin(
                    email=master_admin_email,
                    name='Master Administrator',
                    is_active=True
                )
                db.session.add(master_admin)
                logging.info(f"✅ Created master admin user: {master_admin_email}")
            else:
                logging.info(f"✅ Master admin user already exists: {master_admin_email}")
            
            # Ensure the master admin has a User record too
            existing_user = User.query.filter_by(email=master_admin_email).first()
            if not existing_user:
                user = User(
                    email=master_admin_email,
                    role='Admin'
                )
                db.session.add(user)
                logging.info(f"✅ Created user record for master admin: {master_admin_email}")
            
            # For production, create a demo workspace if no workspaces exist
            if is_production:
                workspace_count = Workspace.query.count()
                if workspace_count == 0:
                    logging.info("📊 Creating demo workspace for production testing...")
                    
                    # Get or create demo user
                    demo_user = User.query.filter_by(email='demo@casualworkermanager.com').first()
                    if not demo_user:
                        demo_user = User(
                            email='demo@casualworkermanager.com',
                            profile_picture=''
                        )
                        db.session.add(demo_user)
                        db.session.flush()
                    
                    # Create demo workspace
                    demo_workspace = Workspace(
                        name='Demo Company Ltd',
                        country='Zambia',
                        industry_type='Technology',
                        expected_workers_string='below_100',
                        expected_workers=25,
                        company_phone='+260977123456',
                        company_email='demo@casualworkermanager.com',
                        address='Demo Street, Lusaka, Zambia',
                        created_by=demo_user.id,
                        subscription_status='trial',
                        subscription_tier='starter',
                        trial_end_date=datetime.utcnow() + timedelta(days=30)
                    )
                    
                    db.session.add(demo_workspace)
                    db.session.flush()
                    
                    # Create company for the workspace
                    demo_company = Company(
                        name='Demo Company Ltd',
                        registration_number='DEMO001',
                        address='Demo Street, Lusaka, Zambia',
                        industry='Technology',
                        phone='+260977123456',
                        created_by=demo_user.id,
                        workspace_id=demo_workspace.id
                    )
                    db.session.add(demo_company)
                    
                    # Add user to workspace as admin
                    user_workspace = UserWorkspace(
                        user_id=demo_user.id,
                        workspace_id=demo_workspace.id,
                        role='Admin'
                    )
                    db.session.add(user_workspace)
                    
                    logging.info(f"✅ Created demo workspace: {demo_workspace.name}")
                    logging.info(f"✅ Demo workspace code: {demo_workspace.workspace_code}")
            
            # Commit all changes
            db.session.commit()
            
            logging.info("🎉 Database initialization completed successfully!")
            return True
            
    except Exception as e:
        logging.error(f"❌ Database initialization failed: {str(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        return False

def check_database_health():
    """Check database connectivity and table existence"""
    try:
        from app_init import app, db
        from models import Workspace, User, MasterAdmin
        
        with app.app_context():
            # Test database queries
            user_count = User.query.count()
            workspace_count = Workspace.query.count()
            admin_count = MasterAdmin.query.count()
            
            logging.info(f"📊 Database health check:")
            logging.info(f"   Users: {user_count}")
            logging.info(f"   Workspaces: {workspace_count}")
            logging.info(f"   Master Admins: {admin_count}")
            
            return True
            
    except Exception as e:
        logging.error(f"❌ Database health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database
    success = init_database()
    
    if success:
        print("✅ Database initialization completed successfully")
        exit(0)
    else:
        print("❌ Database initialization failed")
        exit(1)
