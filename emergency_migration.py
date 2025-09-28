#!/usr/bin/env python3
"""
Emergency migration script to add missing columns directly to the database.
This bypasses Alembic and adds the columns manually.
"""

import os
import sys
import psycopg2
import logging

def get_database_connection():
    """Get database connection for Cloud SQL"""
    try:
        # Check if we have the required environment variables
        db_user = os.environ.get('DB_USER', 'postgres')
        db_pass = os.environ.get('DB_PASS', '')
        db_name = os.environ.get('DB_NAME', 'casual_worker_db')
        
        # For Cloud SQL connection
        connection_name = os.environ.get('INSTANCE_CONNECTION_NAME')
        if connection_name:
            # Use Unix socket for Cloud SQL
            host = f'/cloudsql/{connection_name}'
            conn = psycopg2.connect(
                host=host,
                database=db_name,
                user=db_user,
                password=db_pass
            )
        else:
            # Direct connection
            db_host = os.environ.get('DB_HOST', 'localhost')
            conn = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_pass
            )
        
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")
        return None

def add_missing_columns():
    """Add the missing per_day_payout and per_day_currency columns"""
    conn = get_database_connection()
    if not conn:
        print("❌ Could not connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'task' 
            AND column_name IN ('per_day_payout', 'per_day_currency')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        if 'per_day_payout' not in existing_columns:
            print("Adding per_day_payout column...")
            cursor.execute("ALTER TABLE task ADD COLUMN per_day_payout FLOAT")
            print("✅ Added per_day_payout column")
        else:
            print("✅ per_day_payout column already exists")
        
        if 'per_day_currency' not in existing_columns:
            print("Adding per_day_currency column...")
            cursor.execute("ALTER TABLE task ADD COLUMN per_day_currency VARCHAR(10)")
            print("✅ Added per_day_currency column")
        else:
            print("✅ per_day_currency column already exists")
        
        # Commit the changes
        conn.commit()
        print("✅ Database schema updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Emergency Database Migration")
    print("Adding missing per_day_payout and per_day_currency columns...")
    
    if add_missing_columns():
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1)
