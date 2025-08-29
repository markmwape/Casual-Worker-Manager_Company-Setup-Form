#!/usr/bin/env python3
"""
Monitor deployment and test the application
"""

import subprocess
import time
import requests
import json

def check_build_status():
    """Check the latest build status"""
    try:
        result = subprocess.run(
            ["gcloud", "builds", "list", "--limit=1", "--format=json"],
            capture_output=True, text=True, check=True
        )
        builds = json.loads(result.stdout)
        if builds:
            build = builds[0]
            return build['status'], build['id']
        return None, None
    except Exception as e:
        print(f"Error checking build status: {e}")
        return None, None

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get("https://casual-worker-manager-company-setup-form-egtlvbqlka-uc.a.run.app/health", timeout=10)
        return response.status_code, response.json()
    except Exception as e:
        return None, str(e)

def main():
    print("🚀 Monitoring deployment...")
    
    # Wait for build to complete
    while True:
        status, build_id = check_build_status()
        print(f"📦 Build {build_id}: {status}")
        
        if status == "SUCCESS":
            print("✅ Build completed successfully!")
            break
        elif status == "FAILURE":
            print("❌ Build failed!")
            return
        elif status == "TIMEOUT":
            print("⏰ Build timed out!")
            return
        
        print("⏳ Waiting for build to complete...")
        time.sleep(30)
    
    # Test the application
    print("\n🧪 Testing application...")
    for i in range(5):  # Try 5 times
        print(f"Attempt {i+1}/5...")
        status_code, response = test_health_endpoint()
        
        if status_code == 200:
            print("✅ Application is healthy!")
            print(f"Response: {response}")
            return
        else:
            print(f"❌ Health check failed: {status_code}")
            print(f"Response: {response}")
            if i < 4:  # Don't sleep on last attempt
                print("⏳ Waiting before retry...")
                time.sleep(30)
    
    print("❌ Application health check failed after 5 attempts")

if __name__ == "__main__":
    main() 