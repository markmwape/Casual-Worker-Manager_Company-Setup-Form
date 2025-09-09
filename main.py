import logging
import os
import traceback

# Diagnose import issues
try:
    from app_init import app
except Exception:
    traceback.print_exc()
    raise

from gunicorn.app.base import BaseApplication
import routes
from flask import jsonify, request, session, render_template, redirect, url_for
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Firebase config route moved to routes.py to avoid duplication

@app.route('/test_session')
def test_session():
    """Test endpoint to check session functionality"""
    try:
        return jsonify({
            "session_exists": 'user' in session,
            "session_user": session.get('user'),
            "all_session_keys": list(session.keys()),
            "app_secret_key_set": bool(app.secret_key)
        })
    except Exception as e:
        logging.error(f"Error in test_session: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Get port from environment variable (Cloud Run requirement)
    port = int(os.environ.get("PORT", 8080))
    
    options = {
        "bind": f"0.0.0.0:{port}",
        "loglevel": "info",
        "accesslog": "-",
        "timeout": 300,  # Increased timeout for Cloud Run
        "preload": False,  # Disable preload to reduce memory usage
        "workers": 1,  # Single worker for Cloud Run
        "worker_class": "sync",  # Use sync worker class
        "max_requests": 1000,
        "max_requests_jitter": 100,
        "worker_connections": 1000,
        "keepalive": 2,
        "max_requests_jitter": 50
    }
    StandaloneApplication(app, options).run()