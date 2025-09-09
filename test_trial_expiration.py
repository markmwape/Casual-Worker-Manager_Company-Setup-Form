#!/usr/bin/env python3
"""
Test script to manually expire a trial for testing purposes.

Usage:
    python test_trial_expiration.py <workspace_id>
    
This will set the trial_end_date to yesterday, making the trial expired.
"""

import sys
from datetime import datetime, timedelta
import os
import sqlite3

def expire_trial(workspace_id):
    """Manually expire a workspace trial for testing"""
    
    # Database connection
    db_path = 'database.sqlite'  # Adjust if your database is elsewhere
    
    if not os.path.exists(db_path):
        db_path = 'instance/database.sqlite'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Make sure you're running this from the project root.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if workspace exists
        cursor.execute("SELECT id, name, trial_end_date, subscription_status FROM workspace WHERE id = ?", (workspace_id,))
        workspace = cursor.fetchone()
        
        if not workspace:
            print(f"❌ Workspace with ID {workspace_id} not found.")
            conn.close()
            return False
        
        print(f"📋 Found workspace: {workspace[1]}")
        print(f"   Current trial end: {workspace[2]}")
        print(f"   Current status: {workspace[3]}")
        
        # Set trial to expired (yesterday)
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        cursor.execute(
            "UPDATE workspace SET trial_end_date = ? WHERE id = ?",
            (yesterday.isoformat(), workspace_id)
        )
        
        conn.commit()
        conn.close()
        
        print(f"✅ Trial expired successfully!")
        print(f"   New trial end date: {yesterday.isoformat()}")
        print(f"   The workspace should now show as expired when you refresh the app.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def list_workspaces():
    """List all workspaces for reference"""
    
    db_path = 'database.sqlite'
    if not os.path.exists(db_path):
        db_path = 'instance/database.sqlite'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, trial_end_date, subscription_status 
            FROM workspace 
            ORDER BY created_at DESC
        """)
        
        workspaces = cursor.fetchall()
        
        if not workspaces:
            print("📝 No workspaces found.")
            return
        
        print("\n📋 Available Workspaces:")
        print("-" * 60)
        for ws in workspaces:
            trial_status = "EXPIRED" if ws[2] and datetime.fromisoformat(ws[2]) < datetime.utcnow() else "ACTIVE"
            print(f"ID: {ws[0]} | Name: {ws[1]} | Status: {ws[3]} | Trial: {trial_status}")
        print("-" * 60)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🔧 Trial Expiration Test Tool")
        print("\nUsage:")
        print("  python test_trial_expiration.py <workspace_id>  # Expire specific workspace")
        print("  python test_trial_expiration.py list            # List all workspaces")
        print("\nExample:")
        print("  python test_trial_expiration.py 1")
        sys.exit(1)
    
    if sys.argv[1] == "list":
        list_workspaces()
    else:
        try:
            workspace_id = int(sys.argv[1])
            expire_trial(workspace_id)
        except ValueError:
            print("❌ Workspace ID must be a number")
            sys.exit(1)
