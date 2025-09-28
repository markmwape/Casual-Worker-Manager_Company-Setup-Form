#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_init import app, db
from models import User

# Use application context
with app.app_context():
    # Check database connection and user table
    print("✅ Database connection test - checking if user table is accessible")
    
    try:
        # Test basic query
        user_count = User.query.count()
        print(f"✅ User table accessible. Current user count: {user_count}")
        
        # List all users for debugging
        all_users = User.query.all()
        for user in all_users:
            print(f"   User: {user.email} (ID: {user.id}, Role: {user.role})")
            
    except Exception as e:
        print(f"❌ Error accessing user table: {e}")
        
    print("✅ System is ready for admin user creation during workspace setup")
