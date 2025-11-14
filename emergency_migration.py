#!/usr/bin/env python3
"""
Emergency migration script for production deployments
This script handles critical database updates that need to run before the main application starts
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables"""
    # Production: Use Cloud SQL
    db_user = os.environ.get('DB_USER', 'cwuser')
    db_pass = os.environ.get('DB_PASS', '')
    db_name = os.environ.get('DB_NAME', 'cw_manager')
    
    # For Cloud SQL Proxy
    connection_name = os.environ.get('INSTANCE_CONNECTION_NAME')
    if connection_name:
        return f'postgresql://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{connection_name}'
    else:
        db_host = os.environ.get('DB_HOST', 'localhost')
        return f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}'

def run_emergency_migration():
    """Run emergency database migrations"""
    try:
        database_url = get_database_url()
        logger.info(f"Connecting to database...")
        
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Add any critical columns that might be missing
            migrations = [
                ("workspace", "subscription_tier", "VARCHAR(50)", "trial"),
                ("workspace", "subscription_status", "VARCHAR(50)", "active"),
                ("workspace", "trial_end_date", "DATETIME", None),
                ("workspace", "stripe_customer_id", "VARCHAR(255)", None),
                ("workspace", "stripe_subscription_id", "VARCHAR(255)", None),
                ("user", "language_preference", "VARCHAR(10)", "en")
            ]
            
            for table_name, column_name, column_type, default_value in migrations:
                try:
                    if default_value:
                        sql = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_type} DEFAULT '{default_value}'"
                    else:
                        sql = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
                    
                    connection.execute(text(sql))
                    connection.commit()
                    logger.info(f"✅ Added column {column_name} to {table_name} table")
                except Exception as e:
                    logger.info(f"Column {column_name} already exists or couldn't be added: {str(e)}")
                    continue
            
            logger.info("✅ Emergency migration completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Emergency migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_emergency_migration()
    sys.exit(0 if success else 1)
