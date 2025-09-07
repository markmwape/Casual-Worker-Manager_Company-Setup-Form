#!/usr/bin/env python3
"""
Check tables and create activity_log table via Cloud SQL proxy
"""

import psycopg2
import sys

def check_and_create_activity_log_table():
    """Check existing tables and create the activity_log table"""
    
    try:
        print("Connecting to Cloud SQL via proxy...")
        conn = psycopg2.connect(
            host="127.0.0.1",
            database="cw_manager",
            user="postgres",
            password="temppass123",
            port=5432
        )
        
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("Existing tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if activity_log already exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'activity_log'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("\n✓ activity_log table already exists")
            return True
            
        print("\nCreating activity_log table...")
        
        # Check if users table exists for foreign key
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """)
        
        users_table_exists = cursor.fetchone()[0]
        
        if users_table_exists:
            # Create with foreign key constraint
            create_table_sql = """
            CREATE TABLE activity_log (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                action VARCHAR(255) NOT NULL,
                description TEXT,
                ip_address VARCHAR(45),
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
            print("Creating with foreign key constraint to users table...")
        else:
            # Create without foreign key constraint
            create_table_sql = """
            CREATE TABLE activity_log (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                action VARCHAR(255) NOT NULL,
                description TEXT,
                ip_address VARCHAR(45),
                user_agent TEXT
            );
            """
            print("Creating without foreign key constraint (users table not found)...")
        
        cursor.execute(create_table_sql)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_activity_log_timestamp ON activity_log(timestamp);")
        cursor.execute("CREATE INDEX idx_activity_log_user_id ON activity_log(user_id);")
        
        conn.commit()
        print("✓ Successfully created activity_log table with indexes")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = check_and_create_activity_log_table()
    sys.exit(0 if success else 1)
