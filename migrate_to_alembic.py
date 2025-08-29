#!/usr/bin/env python3
"""
Migration helper script to transition from manual SQL migrations to Alembic.
This script helps you safely migrate your existing database to use Alembic.
"""

import os
import sys
import subprocess
from app_init import app
from models import db

def check_alembic_status():
    """Check the current status of Alembic migrations"""
    print("🔍 Checking Alembic status...")
    try:
        result = subprocess.run(
            ["python3", "-m", "alembic", "current"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            print("✅ Alembic is properly configured")
            print(f"Current revision: {result.stdout.strip()}")
            return True
        else:
            print("❌ Alembic status check failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking Alembic status: {e}")
        return False

def check_database_tables():
    """Check what tables exist in the database"""
    print("\n📋 Checking existing database tables...")
    try:
        with app.app_context():
            # Get list of existing tables
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            print(f"Found {len(existing_tables)} tables:")
            for table in existing_tables:
                print(f"  - {table}")
            
            return existing_tables
    except Exception as e:
        print(f"❌ Error checking database tables: {e}")
        return []

def backup_existing_migrations():
    """Backup the existing SQL migration files"""
    print("\n💾 Backing up existing SQL migrations...")
    migrations_dir = "migrations"
    backup_dir = "migrations_backup"
    
    if os.path.exists(migrations_dir):
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Copy all SQL files to backup
        import shutil
        for file in os.listdir(migrations_dir):
            if file.endswith('.sql'):
                src = os.path.join(migrations_dir, file)
                dst = os.path.join(backup_dir, file)
                shutil.copy2(src, dst)
                print(f"  Backed up: {file}")
        
        print(f"✅ SQL migrations backed up to {backup_dir}/")
    else:
        print("ℹ️  No existing migrations directory found")

def run_initial_migration():
    """Run the initial Alembic migration"""
    print("\n🚀 Running initial Alembic migration...")
    try:
        # First, mark the current state as the initial migration
        result = subprocess.run(
            ["python3", "-m", "alembic", "stamp", "head"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            print("✅ Successfully stamped current database state")
            return True
        else:
            print("❌ Failed to stamp database state")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running initial migration: {e}")
        return False

def create_migration_guide():
    """Create a guide for future migrations"""
    guide_content = """# Migration Guide

## Transitioning from Manual SQL Migrations to Alembic

Your application has been successfully migrated to use Alembic for database migrations. Here's how to work with migrations going forward:

### Current Status
- ✅ Alembic is configured and working
- ✅ Your current database schema is captured in the initial migration
- ✅ Old SQL migrations are backed up in `migrations_backup/`

### Making Schema Changes

1. **Update your models** in `models.py`
2. **Generate a migration**:
   ```bash
   python3 -m alembic revision --autogenerate -m "Description of changes"
   ```
3. **Review the generated migration** in `alembic/versions/`
4. **Apply the migration**:
   ```bash
   python3 -m alembic upgrade head
   ```

### Useful Commands

- Check current migration status: `python3 -m alembic current`
- View migration history: `python3 -m alembic history`
- Downgrade to previous version: `python3 -m alembic downgrade -1`
- Upgrade to latest: `python3 -m alembic upgrade head`

### Environment Variables

Make sure these environment variables are set for Cloud SQL:
- `DB_USER`: Database username
- `DB_PASS`: Database password  
- `DB_NAME`: Database name
- `DB_HOST`: Database host (for direct connection)
- `CLOUD_SQL_CONNECTION_NAME`: Cloud SQL connection name (for App Engine)

### Important Notes

- **Never use `db.create_all()` in production** - always use migrations
- **Always test migrations** on a copy of your production data
- **Backup your database** before running migrations in production
- **Review auto-generated migrations** before applying them

### Rollback Plan

If you need to rollback to the old system:
1. Restore your database from backup
2. Copy SQL files from `migrations_backup/` back to `migrations/`
3. Use the old `run_migrations.py` script

### Next Steps

1. Test the migration system in development
2. Update your deployment scripts to use Alembic
3. Consider removing the old migration files once you're confident
"""
    
    with open("MIGRATION_GUIDE.md", "w") as f:
        f.write(guide_content)
    
    print("✅ Created MIGRATION_GUIDE.md")

def main():
    """Main migration process"""
    print("🚀 Casual Worker Manager - Alembic Migration Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("alembic.ini"):
        print("❌ alembic.ini not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Step 1: Check Alembic status
    if not check_alembic_status():
        print("❌ Alembic is not properly configured")
        sys.exit(1)
    
    # Step 2: Check database tables
    existing_tables = check_database_tables()
    if not existing_tables:
        print("❌ No tables found in database")
        sys.exit(1)
    
    # Step 3: Backup existing migrations
    backup_existing_migrations()
    
    # Step 4: Run initial migration
    if not run_initial_migration():
        print("❌ Failed to run initial migration")
        sys.exit(1)
    
    # Step 5: Create migration guide
    create_migration_guide()
    
    print("\n🎉 Migration to Alembic completed successfully!")
    print("\n📋 Summary:")
    print("  ✅ Alembic is configured and working")
    print("  ✅ Your current schema is captured")
    print("  ✅ Old migrations are backed up")
    print("  ✅ Migration guide created")
    print("\n📖 Next steps:")
    print("  1. Read MIGRATION_GUIDE.md for usage instructions")
    print("  2. Test the migration system")
    print("  3. Update your deployment process")
    print("  4. Consider removing old migration files once confident")

if __name__ == "__main__":
    main() 