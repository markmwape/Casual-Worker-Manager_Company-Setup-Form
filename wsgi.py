import logging
import os

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("🚀 Starting WSGI application...")
    logger.info(f"📂 Working directory: {os.getcwd()}")
    logger.info(f"📄 Python path: {os.sys.path}")
    
    from app_init import app
    logger.info("✅ Flask app imported successfully")
    
    # Test that the app is working
    with app.app_context():
        logger.info("✅ Flask app context is working")
        
except Exception as e:
    logger.error(f"❌ Failed to import Flask app: {str(e)}")
    import traceback
    logger.error(f"📋 Full traceback:\n{traceback.format_exc()}")
    
    # Try to provide a fallback simple app for debugging
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def health_check():
        return {"status": "error", "message": "App failed to initialize properly"}
    
    @app.route('/health')
    def health():
        return {"status": "degraded", "message": "Running in fallback mode"}
    
    logger.warning("⚠️  Running in fallback mode due to initialization error")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
