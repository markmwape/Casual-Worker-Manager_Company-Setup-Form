#!/usr/bin/env python3
"""
Apply language_preference migration to production database
This script safely adds the language_preference column if it doesn't exist
"""

import os
import sys
from sqlalchemy import text, inspect
from app_init import app, db

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def apply_migration():
    """Apply the language_preference migration"""
    print("\n" + "=" * 80)
    print("APPLYING LANGUAGE PREFERENCE MIGRATION")
    print("=" * 80 + "\n")
    
    with app.app_context():
        engine = db.engine
        
        # Check if column already exists
        if check_column_exists(engine, 'user', 'language_preference'):
            print("✅ Column 'language_preference' already exists in user table")
            return True
        
        print("⏳ Column 'language_preference' not found. Creating it...\n")
        
        try:
            # Execute the migration
            with engine.connect() as connection:
                # For PostgreSQL, we use IF NOT EXISTS
                sql = text("""
                    ALTER TABLE "user"
                    ADD COLUMN IF NOT EXISTS language_preference VARCHAR(10) DEFAULT 'en' NOT NULL
                """)
                connection.execute(sql)
                connection.commit()
                
                print("✅ Successfully added 'language_preference' column to user table")
                print("   • Column: language_preference")
                print("   • Type: VARCHAR(10)")
                print("   • Default: 'en'")
                print("   • Nullable: False\n")
                
                return True
                
        except Exception as e:
            print(f"❌ Error applying migration: {str(e)}\n")
            return False

def verify_migration():
    """Verify the migration was successful"""
    print("Verifying migration...\n")
    
    with app.app_context():
        try:
            from models import User
            # Try to query the user table with the new column
            user_count = User.query.count()
            print(f"✅ Database query successful!")
            print(f"   • Total users in database: {user_count}\n")
            return True
        except Exception as e:
            print(f"❌ Verification failed: {str(e)}\n")
            return False

if __name__ == '__main__':
    print("\n🚀 Starting language preference migration...\n")
    
    # Apply migration
    migration_success = apply_migration()
    
    if migration_success:
        # Verify
        verify_success = verify_migration()
        
        if verify_success:
            print("=" * 80)
            print("✅ MIGRATION COMPLETE!")
            print("=" * 80)
            print("\n✨ You can now use the application with multi-language support!")
            print("   Users can switch languages using the 🌐 language switcher.\n")
            sys.exit(0)
        else:
            print("⚠️  Migration applied but verification failed.\n")
            sys.exit(1)
    else:
        print("❌ Migration failed.\n")
        sys.exit(1)
