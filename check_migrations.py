#!/usr/bin/env python3
"""
Check which migrations have been applied
"""
import os
import sys
import sqlite3

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_migrations():
    """Check which migrations have been applied"""
    try:
        # Connect to database
        conn = sqlite3.connect('database.sqlite')
        cursor = conn.cursor()
        
        # Get applied migrations
        cursor.execute('SELECT filename, applied_at FROM migrations ORDER BY applied_at')
        applied_migrations = cursor.fetchall()
        
        print("✅ Applied Migrations:")
        for filename, applied_at in applied_migrations:
            print(f"  - {filename} (applied: {applied_at})")
        
        # Get all migration files
        migration_files = sorted([f for f in os.listdir('migrations') if f.endswith('.sql')])
        
        print(f"\n📁 Total Migration Files: {len(migration_files)}")
        print("📋 All Migration Files:")
        for filename in migration_files:
            status = "✅ Applied" if any(filename in applied[0] for applied in applied_migrations) else "⏳ Pending"
            print(f"  - {filename} ({status})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking migrations: {str(e)}")

if __name__ == "__main__":
    check_migrations() 