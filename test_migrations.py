#!/usr/bin/env python3
"""
Test migrations system
"""
import os
import sys
import sqlite3
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_init import app
from abilities import apply_sqlite_migrations

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_migrations():
    """Test the migrations system"""
    try:
        with app.app_context():
            # Get database path
            db_path = str(app.config['SQLALCHEMY_DATABASE_URI']).replace('sqlite:///', '')
            print(f"Database path: {db_path}")
            print(f"Database file exists: {os.path.exists(db_path)}")
            
            # Connect to database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create migrations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL UNIQUE,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            
            # Check if migrations table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
            migrations_table = cursor.fetchone()
            print(f"Migrations table exists: {migrations_table is not None}")
            
            # Get applied migrations
            cursor.execute('SELECT filename FROM migrations')
            applied_migrations = cursor.fetchall()
            print(f"Applied migrations: {applied_migrations}")
            
            conn.close()
            
            # Test the full migration system
            print("\nTesting full migration system...")
            from models import db
            apply_sqlite_migrations(db.engine, db.Model, 'migrations')
            
    except Exception as e:
        logger.error(f"Error testing migrations: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_migrations() 