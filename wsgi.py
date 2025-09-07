import logging
import os

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting WSGI application...")
    from app_init import app
    logger.info("Flask app imported successfully")
except Exception as e:
    logger.error(f"Failed to import Flask app: {str(e)}")
    import traceback
    traceback.print_exc()
    raise

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
