#!/usr/bin/env python3
"""
Migration runner for Casual Worker Manager
This script runs migrations on both local SQLite and Cloud SQL databases.
"""

import os
import sys
from abilities import apply_sqlite_migrations
from app_init import app
from models import db

def run_migrations():
    """Run database migrations"""
    
    print("🔄 Running database migrations...")
    
    with app.app_context():
        try:
            # Apply migrations
            apply_sqlite_migrations()
            print("✅ Migrations completed successfully!")
            
            # Verify tables were created
            from models import User, Company, Workspace, UserWorkspace, MasterAdmin
            tables = db.engine.table_names()
            print(f"📋 Available tables: {', '.join(tables)}")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            return False
    
    return True

def check_database_connection():
    """Check database connection and configuration"""
    
    print("🔍 Checking database configuration...")
    
    # Check if we're using Cloud SQL or SQLite
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    
    if 'postgresql' in db_uri:
        print("📊 Using Cloud SQL (PostgreSQL)")
        print(f"   Host: {os.environ.get('DB_HOST', 'N/A')}")
        print(f"   Database: {os.environ.get('DB_NAME', 'N/A')}")
        print(f"   User: {os.environ.get('DB_USER', 'N/A')}")
    else:
        print("📊 Using local SQLite")
        print(f"   Database file: database.sqlite")
    
    # Test connection
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))
                print("✅ Database connection successful!")
                return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Casual Worker Manager - Database Migration Tool")
    print("=" * 50)
    
    if not check_database_connection():
        print("\n❌ Cannot proceed without database connection")
        sys.exit(1)
    
    if run_migrations():
        print("\n🎉 All migrations completed successfully!")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1) 