#!/usr/bin/env python3
"""
Create activity_log table via Cloud SQL proxy
"""

import psycopg2
import sys

def create_activity_log_table():
    """Create the activity_log table via proxy"""
    
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
        
        # Check if table already exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'activity_log'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("✓ activity_log table already exists")
            return True
            
        print("Creating activity_log table...")
        
        # Create the activity_log table
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
    success = create_activity_log_table()
    sys.exit(0 if success else 1)
