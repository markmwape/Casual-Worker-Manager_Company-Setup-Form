#!/usr/bin/env python3
"""
Direct script to create activity_log table in Cloud SQL
"""

import psycopg2
import sys

def create_activity_log_table():
    """Create the activity_log table directly in Cloud SQL"""
    
    # Cloud SQL connection parameters
    host = "34.41.184.5"
    database = "casual_worker_db"
    user = "postgres"
    password = ""  # Empty password as configured
    
    try:
        print(f"Connecting to Cloud SQL at {host}...")
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
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
        
        # Create index for better performance
        cursor.execute("CREATE INDEX idx_activity_log_timestamp ON activity_log(timestamp);")
        cursor.execute("CREATE INDEX idx_activity_log_user_id ON activity_log(user_id);")
        
        conn.commit()
        print("✓ Successfully created activity_log table with indexes")
        
        # Verify table creation
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'activity_log'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col_name, data_type in columns:
            print(f"  {col_name}: {data_type}")
        
        return True
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
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
