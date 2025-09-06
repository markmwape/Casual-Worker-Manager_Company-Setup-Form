#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_init import app, db
from models import User, Workspace, UserWorkspace, Company

# Use application context
with app.app_context():
    # Find the system user
    system_user = User.query.filter_by(email="system@workspace.com").first()
    
    if system_user:
        print(f"Found system user: {system_user.email} (ID: {system_user.id})")
        
        # Check if any workspaces are owned by the system user
        workspaces_owned = Workspace.query.filter_by(created_by=system_user.id).all()
        if workspaces_owned:
            print(f"⚠️  Found {len(workspaces_owned)} workspaces owned by system user:")
            for workspace in workspaces_owned:
                print(f"   Workspace: {workspace.name} (ID: {workspace.id})")
                
                # Find if there are any real admin users in this workspace
                admin_users = UserWorkspace.query.filter_by(
                    workspace_id=workspace.id, 
                    role='Admin'
                ).join(User).filter(User.email != 'system@workspace.com').all()
                
                if admin_users:
                    # Transfer ownership to the first real admin
                    new_owner = admin_users[0].user
                    workspace.created_by = new_owner.id
                    print(f"   → Transferred ownership to {new_owner.email}")
                else:
                    print(f"   → No real admin users found for workspace {workspace.name}")
                    print(f"   → Workspace will be orphaned - manual intervention needed")
        
        # Remove system user from all user_workspace relationships
        user_workspaces = UserWorkspace.query.filter_by(user_id=system_user.id).all()
        for uw in user_workspaces:
            print(f"Removing system user from workspace: {uw.workspace.name}")
            db.session.delete(uw)
        
        # Check for companies created by system user
        companies_owned = Company.query.filter_by(created_by=system_user.id).all()
        for company in companies_owned:
            workspace = Workspace.query.get(company.workspace_id)
            if workspace:
                company.created_by = workspace.created_by
                print(f"Updated company {company.name} ownership to workspace owner")
        
        # Remove the system user
        db.session.delete(system_user)
        db.session.commit()
        
        print("✅ System user removed successfully!")
        
        # Show remaining users
        remaining_users = User.query.all()
        print(f"\nRemaining users ({len(remaining_users)}):")
        for user in remaining_users:
            print(f"   User: {user.email} (ID: {user.id}, Role: {user.role})")
            
    else:
        print("✅ No system user found - already cleaned up")
