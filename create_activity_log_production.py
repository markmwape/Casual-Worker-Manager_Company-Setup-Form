#!/usr/bin/env python3
"""
Script to create the ActivityLog table in production PostgreSQL database
"""

import os
import psycopg2
from psycopg2 import sql
import logging

def create_activity_log_table():
    """Create the ActivityLog table in production database"""
    
    # Database connection parameters
    db_host = os.environ.get('DB_HOST')
    db_name = os.environ.get('DB_NAME', 'casualworkermanager')
    db_user = os.environ.get('DB_USER', 'postgres')
    db_pass = os.environ.get('DB_PASS')
    connection_name = os.environ.get('INSTANCE_CONNECTION_NAME')
    
    if not db_pass:
        print("❌ DB_PASS environment variable not set")
        return False
    
    try:
        # Try Cloud SQL socket connection first
        if connection_name:
            conn_str = f"host=/cloudsql/{connection_name} dbname={db_name} user={db_user} password={db_pass}"
            print(f"🔌 Attempting Cloud SQL socket connection...")
        else:
            # Fallback to direct connection
            if not db_host:
                print("❌ Neither INSTANCE_CONNECTION_NAME nor DB_HOST set")
                return False
            conn_str = f"host={db_host} dbname={db_name} user={db_user} password={db_pass}"
            print(f"🔌 Attempting direct connection to {db_host}...")
        
        conn = psycopg2.connect(conn_str)
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
            print("✅ ActivityLog table already exists")
            
            # Check the structure
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'activity_log' 
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            print("📊 Current table structure:")
            for col_name, col_type in columns:
                print(f"   - {col_name}: {col_type}")
                
        else:
            print("🔧 Creating ActivityLog table...")
            
            # Create the table
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
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workspace_id) REFERENCES workspace (id),
                FOREIGN KEY (user_id) REFERENCES "user" (id)
            );
            """
            
            cursor.execute(create_table_sql)
            
            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_activity_log_workspace_id ON activity_log(workspace_id);",
                "CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_activity_log_action_type ON activity_log(action_type);",
                "CREATE INDEX IF NOT EXISTS idx_activity_log_resource_type ON activity_log(resource_type);"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
            print("✅ ActivityLog table created successfully!")
        
        # Test the table
        cursor.execute("SELECT COUNT(*) FROM activity_log;")
        count = cursor.fetchone()[0]
        print(f"📈 Current record count: {count}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting ActivityLog table setup...")
    success = create_activity_log_table()
    if success:
        print("🎉 ActivityLog table setup completed!")
    else:
        print("💥 ActivityLog table setup failed!")
