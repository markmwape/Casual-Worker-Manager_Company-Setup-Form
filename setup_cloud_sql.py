#!/usr/bin/env python3
"""
Setup script for Cloud SQL database
This script helps you set up a Cloud SQL instance for your Casual Worker Manager app.
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def setup_cloud_sql():
    """Set up Cloud SQL instance and database"""
    
    print("🚀 Setting up Cloud SQL for Casual Worker Manager...")
    
    # Get project ID
    project_id = input("Enter your Google Cloud Project ID: ").strip()
    if not project_id:
        print("❌ Project ID is required")
        return False
    
    # Set project
    run_command(f"gcloud config set project {project_id}", "Setting project")
    
    # Enable required APIs
    run_command("gcloud services enable sqladmin.googleapis.com", "Enabling Cloud SQL Admin API")
    run_command("gcloud services enable cloudbuild.googleapis.com", "Enabling Cloud Build API")
    
    # Create Cloud SQL instance
    instance_name = "casual-worker-db"
    region = "us-central1"
    
    print(f"📦 Creating Cloud SQL instance '{instance_name}' in {region}...")
    
    # Create the instance
    create_instance_cmd = f"""
    gcloud sql instances create {instance_name} \
        --database-version=POSTGRES_14 \
        --tier=db-f1-micro \
        --region={region} \
        --storage-type=SSD \
        --storage-size=10GB \
        --availability-type=zonal \
        --authorized-networks=0.0.0.0/0
    """
    
    if not run_command(create_instance_cmd, "Creating Cloud SQL instance"):
        return False
    
    # Set root password
    root_password = input("Enter a root password for the database: ").strip()
    if not root_password:
        print("❌ Root password is required")
        return False
    
    run_command(f"gcloud sql users set-password postgres --instance={instance_name} --password={root_password}", 
                "Setting root password")
    
    # Create database
    db_name = "casual_worker_db"
    run_command(f"gcloud sql databases create {db_name} --instance={instance_name}", 
                f"Creating database '{db_name}'")
    
    # Create application user
    app_user = "casual_worker_user"
    app_password = input("Enter a password for the application user: ").strip()
    if not app_password:
        print("❌ Application user password is required")
        return False
    
    run_command(f"gcloud sql users create {app_user} --instance={instance_name} --password={app_password}", 
                f"Creating application user '{app_user}'")
    
    # Get connection info
    connection_name = f"{project_id}:{region}:{instance_name}"
    
    print("\n🎉 Cloud SQL setup completed!")
    print("\n📋 Next steps:")
    print("1. Update your deploy.sh script with these environment variables:")
    print(f"   CLOUD_SQL_CONNECTION_NAME={connection_name}")
    print(f"   DB_USER={app_user}")
    print(f"   DB_PASS={app_password}")
    print(f"   DB_NAME={db_name}")
    print(f"   DB_HOST=localhost")
    
    print("\n2. Update your Cloud Run deployment to include these environment variables")
    print("\n3. Run your migrations to create the database schema")
    
    return True

if __name__ == "__main__":
    setup_cloud_sql() 