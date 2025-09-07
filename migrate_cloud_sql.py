#!/usr/bin/env python3
"""
Script to run Alembic migrations against Cloud SQL
Set your Cloud SQL environment variables before running this script.
"""

import os
import subprocess
import sys
from app_init import app
from models import db

def main():
    print("🚀 Cloud SQL Migration Script")
    print("=" * 40)
    
    # Check if we have the required environment variables
    required_vars = ['INSTANCE_CONNECTION_NAME', 'DB_USER', 'DB_PASS', 'DB_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables and try again:")
        print("export INSTANCE_CONNECTION_NAME='your-project:region:instance-name'")
        print("export DB_USER='your-db-user'")
        print("export DB_PASS='your-db-password'")
        print("export DB_NAME='your-db-name'")
        sys.exit(1)
    
    # Set K_SERVICE to trigger Cloud SQL mode
    os.environ['K_SERVICE'] = 'migration-script'
    
    print("🔍 Cloud SQL Configuration:")
    print(f"   Connection Name: {os.environ.get('INSTANCE_CONNECTION_NAME')}")
    print(f"   Database: {os.environ.get('DB_NAME')}")
    print(f"   User: {os.environ.get('DB_USER')}")
    
    # Test database connection
    print("\n🔗 Testing database connection...")
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT 1"))
                print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\nMake sure:")
        print("1. Cloud SQL instance is running")
        print("2. Cloud SQL Auth proxy is running (if needed)")
        print("3. Your IP is whitelisted")
        print("4. Database user has proper permissions")
        sys.exit(1)
    
    # Check if activity_log table exists
    print("\n🔍 Checking for activity_log table...")
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT COUNT(*) FROM activity_log LIMIT 1"))
                count = result.scalar()
                print(f"✅ activity_log table exists with {count} records")
                print("No migration needed!")
                return
    except Exception as e:
        if "does not exist" in str(e) or "relation" in str(e):
            print("📋 activity_log table does not exist - migration needed")
        else:
            print(f"❌ Error checking table: {str(e)}")
            sys.exit(1)
    
    # Run Alembic migrations
    print("\n🔄 Running Alembic migrations...")
    try:
        result = subprocess.run(
            ["python3", "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            print("✅ Migrations completed successfully!")
            print(result.stdout)
        else:
            print("❌ Migration failed!")
            print(f"Error: {result.stderr}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        sys.exit(1)
    
    # Verify activity_log table was created
    print("\n🔍 Verifying activity_log table...")
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT COUNT(*) FROM activity_log"))
                count = result.scalar()
                print(f"✅ activity_log table created successfully! ({count} records)")
    except Exception as e:
        print(f"❌ Error verifying table: {str(e)}")
        sys.exit(1)
    
    print("\n🎉 Cloud SQL migration completed successfully!")
    print("Your deployed app should now be able to display activity logs.")

if __name__ == "__main__":
    main()
