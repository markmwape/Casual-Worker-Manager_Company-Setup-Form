#!/usr/bin/env python3
"""
Minimal database initialization for Cloud Run
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database_minimal():
    """Minimal database initialization that won't crash the service"""
    try:
        # Add app directory to path
        import sys
        sys.path.insert(0, '/app')
        
        from app_init import app, db
        
        with app.app_context():
            logger.info("🔧 Creating database tables...")
            
            # Just create tables - don't do complex operations
            db.create_all()
            logger.info("✅ Database tables created")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        # Don't crash - let the service start anyway
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting minimal database initialization...")
    success = init_database_minimal()
    
    if success:
        logger.info("✅ Database initialization completed")
    else:
        logger.warning("⚠️ Database initialization failed but continuing")
    
    # Always exit successfully so the service can start
    exit(0)
