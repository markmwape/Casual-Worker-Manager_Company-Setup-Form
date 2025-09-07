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
        from app_init import app
        import routes  # This imports all routes
        
        logger.info("Flask app and routes imported successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create app: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

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
