#!/usr/bin/env python3
"""
Simple startup script for Cloud Run deployment
"""
import os
import sys

def main():
    """Main entry point"""
    try:
        # Import the Flask app
        from main import app
        
        # Get port from environment variable
        port = int(os.environ.get("PORT", 8080))
        
        # Run the app
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
