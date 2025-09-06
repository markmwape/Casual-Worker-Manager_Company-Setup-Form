#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_init import app, db
from models import User

# Use application context
with app.app_context():
    # Check if system user exists
    system_user = User.query.filter_by(email="system@workspace.com").first()
    
    if not system_user:
        # Create system user
        system_user = User(
            email="system@workspace.com",
            profile_picture="",
            role="Admin"
        )
        db.session.add(system_user)
        db.session.commit()
        print("✅ System user created successfully!")
    else:
        print("✅ System user already exists")
        
    print(f"System user ID: {system_user.id}")
