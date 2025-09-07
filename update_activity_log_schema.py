#!/usr/bin/env python3
"""
Update activity_log table to match the ActivityLog model
"""

import psycopg2
import sys

def update_activity_log_table():
    """Update the activity_log table to match the model"""
    
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
        
        print("Updating activity_log table schema...")
        
        # Drop and recreate the table with proper schema
        cursor.execute("DROP TABLE IF EXISTS activity_log CASCADE;")
        
        create_table_sql = """
        CREATE TABLE activity_log (
            id SERIAL PRIMARY KEY,
            workspace_id INTEGER NOT NULL,
            user_id INTEGER,
            user_email VARCHAR(150) NOT NULL,
            action_type VARCHAR(50) NOT NULL,
            resource_type VARCHAR(50) NOT NULL,
            resource_id INTEGER,
            description TEXT NOT NULL,
            details TEXT,
            ip_address VARCHAR(45),
            user_agent TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_sql)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX idx_activity_log_workspace_id ON activity_log(workspace_id);")
        cursor.execute("CREATE INDEX idx_activity_log_user_id ON activity_log(user_id);")
        cursor.execute("CREATE INDEX idx_activity_log_created_at ON activity_log(created_at);")
        cursor.execute("CREATE INDEX idx_activity_log_action_type ON activity_log(action_type);")
        cursor.execute("CREATE INDEX idx_activity_log_resource_type ON activity_log(resource_type);")
        
        conn.commit()
        print("✓ Successfully updated activity_log table schema")
        
        # Grant permissions to cwuser
        cursor.execute('GRANT ALL PRIVILEGES ON TABLE activity_log TO cwuser;')
        cursor.execute('GRANT USAGE, SELECT ON SEQUENCE activity_log_id_seq TO cwuser;')
        conn.commit()
        print("✓ Granted permissions to cwuser")
        
        # Verify table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'activity_log'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col_name, data_type, nullable in columns:
            print(f"  {col_name}: {data_type} {'NULL' if nullable == 'YES' else 'NOT NULL'}")
        
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
    success = update_activity_log_table()
    sys.exit(0 if success else 1)
