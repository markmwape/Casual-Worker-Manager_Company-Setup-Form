#!/usr/bin/env python3
"""
Alembic Migration Runner for Casual Worker Manager
This script runs Alembic migrations on both local SQLite and Cloud SQL databases.
"""

import os
import sys
import subprocess
from app_init import app
from models import db

def check_database_connection():
    """Check database connection and configuration"""
    
    print("🔍 Checking database configuration...")
    
    # Check if we're using Cloud SQL or SQLite
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    
    if 'postgresql' in db_uri:
        print("📊 Using Cloud SQL (PostgreSQL)")
        print(f"   Host: {os.environ.get('DB_HOST', 'N/A')}")
        print(f"   Database: {os.environ.get('DB_NAME', 'N/A')}")
        print(f"   User: {os.environ.get('DB_USER', 'cwuser')}")
        print(f"   Connection Name: {os.environ.get('CLOUD_SQL_CONNECTION_NAME', 'N/A')}")
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

def check_alembic_status():
    """Check Alembic migration status"""
    print("\n🔍 Checking Alembic migration status...")
    try:
        result = subprocess.run(
            ["python3", "-m", "alembic", "current"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            current_revision = result.stdout.strip()
            print(f"✅ Current migration revision: {current_revision}")
            return True
        else:
            print("❌ Failed to get Alembic status")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking Alembic status: {e}")
        return False

def run_migrations():
    """Run Alembic migrations"""
    
    print("\n🔄 Running Alembic migrations...")
    
    try:
        # Run alembic upgrade head
        result = subprocess.run(
            ["python3", "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            print("✅ Migrations completed successfully!")
            print(result.stdout)
            return True
        else:
            print("❌ Migration failed!")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

def show_migration_history():
    """Show migration history"""
    print("\n📋 Migration history:")
    try:
        result = subprocess.run(
            ["python3", "-m", "alembic", "history", "--verbose"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ Failed to get migration history")
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Error getting migration history: {e}")

def create_new_migration(description):
    """Create a new migration"""
    print(f"\n🆕 Creating new migration: {description}")
    try:
        result = subprocess.run(
            ["python3", "-m", "alembic", "revision", "--autogenerate", "-m", description],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            print("✅ New migration created successfully!")
            print(result.stdout)
            return True
        else:
            print("❌ Failed to create migration")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating migration: {e}")
        return False

def main():
    """Main migration runner"""
    print("🚀 Casual Worker Manager - Alembic Migration Runner")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("alembic.ini"):
        print("❌ alembic.ini not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Step 1: Check database connection
    if not check_database_connection():
        print("\n❌ Cannot proceed without database connection")
        sys.exit(1)
    
    # Step 2: Check Alembic status
    if not check_alembic_status():
        print("\n❌ Alembic is not properly configured")
        sys.exit(1)
    
    # Step 3: Show migration history
    show_migration_history()
    
    # Step 4: Run migrations
    if run_migrations():
        print("\n🎉 All migrations completed successfully!")
        
        # Show final status
        print("\n📊 Final migration status:")
        subprocess.run(["python3", "-m", "alembic", "current"], cwd=os.getcwd())
        
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)

def create_migration():
    """Create a new migration with description"""
    if len(sys.argv) < 3:
        print("Usage: python3 run_alembic_migrations.py create 'Migration description'")
        sys.exit(1)
    
    description = sys.argv[2]
    print("🚀 Creating new migration...")
    
    if not check_database_connection():
        print("❌ Cannot proceed without database connection")
        sys.exit(1)
    
    if create_new_migration(description):
        print("\n✅ Migration created successfully!")
        print("📝 Next steps:")
        print("  1. Review the generated migration file in alembic/versions/")
        print("  2. Run 'python3 run_alembic_migrations.py' to apply the migration")
    else:
        print("\n❌ Failed to create migration!")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        create_migration()
    else:
        main()