#!/usr/bin/env python3
"""
Startup script for Cloud Run deployment
This script ensures the app starts correctly with proper error handling
"""
import os
import sys
import logging
from gunicorn.app.base import BaseApplication

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask app"""
    try:
        logger.info("Starting application initialization...")
        
        # Import app after logging is configured
        from app_init import app, db
        import routes  # This imports all routes
        
        logger.info("Flask app and routes imported successfully")
        
        # Ensure database tables exist, especially ActivityLog
        ensure_activity_log_table(app, db)
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to create app: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def ensure_activity_log_table(app, db):
    """Ensure the ActivityLog table exists in the database"""
    try:
        with app.app_context():
            # Check if ActivityLog table exists
            from models import ActivityLog
            
            # Try to query the table
            try:
                ActivityLog.query.count()
                logger.info("✅ ActivityLog table exists and is accessible")
                return True
            except Exception as table_error:
                logger.warning(f"ActivityLog table not accessible: {table_error}")
                
                # Try to create the table
                logger.info("🔧 Attempting to create ActivityLog table...")
                
                # Import SQLAlchemy text for raw SQL
                from sqlalchemy import text
                
                # PostgreSQL-compatible CREATE TABLE statement
                create_table_sql = text("""
                CREATE TABLE IF NOT EXISTS activity_log (
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
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """)
                
                # Create indexes
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_activity_log_workspace_id ON activity_log(workspace_id);",
                    "CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id);",
                    "CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at);",
                    "CREATE INDEX IF NOT EXISTS idx_activity_log_action_type ON activity_log(action_type);",
                    "CREATE INDEX IF NOT EXISTS idx_activity_log_resource_type ON activity_log(resource_type);"
                ]
                
                # Execute table creation
                db.session.execute(create_table_sql)
                
                # Execute index creation
                for index_sql in indexes:
                    try:
                        db.session.execute(text(index_sql))
                    except Exception as idx_error:
                        logger.warning(f"Failed to create index: {idx_error}")
                
                db.session.commit()
                logger.info("✅ ActivityLog table created successfully!")
                
                # Verify the table was created
                count = ActivityLog.query.count()
                logger.info(f"📊 ActivityLog table verified with {count} records")
                return True
                
    except Exception as e:
        logger.error(f"❌ Failed to ensure ActivityLog table: {e}")
        # Don't fail the entire app startup for this
        return False

class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.application = app
        self.options = options or {}
        super().__init__()

    def load_config(self):
        # Apply configuration to Gunicorn
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

def main():
    """Main entry point"""
    try:
        # Get port from environment variable
        port = int(os.environ.get("PORT", 8080))
        logger.info(f"Starting server on port {port}")
        
        # Create the Flask app
        app = create_app()
        
        # Configure Gunicorn options
        options = {
            "bind": f"0.0.0.0:{port}",
            "workers": 1,
            "worker_class": "sync",
            "timeout": 300,
            "keepalive": 2,
            "max_requests": 1000,
            "max_requests_jitter": 50,
            "preload_app": False,
            "loglevel": "info",
            "accesslog": "-",
            "errorlog": "-",
        }
        
        logger.info("Starting Gunicorn server...")
        StandaloneApplication(app, options).run()
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
