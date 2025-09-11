#!/usr/bin/env python3
"""
Fix Subscription Tiers Script
=============================

This script updates existing workspaces that have 'basic' subscription_tier 
to 'trial' to fix the display issue where trial users were shown as being
on "Starter Plan" instead of "Free Trial".

Run this once after deploying the tier configuration changes.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_init import app
from models import db, Workspace
from datetime import datetime

def fix_subscription_tiers():
    """Update workspaces with 'basic' tier to 'trial' tier"""
    
    with app.app_context():
        try:
            # Find all workspaces with 'basic' subscription_tier
            basic_workspaces = Workspace.query.filter_by(subscription_tier='basic').all()
            
            print(f"Found {len(basic_workspaces)} workspaces with 'basic' subscription tier")
            
            updated_count = 0
            for workspace in basic_workspaces:
                # Only update if they're still on trial (not paid)
                if workspace.subscription_status == 'trial':
                    print(f"Updating workspace '{workspace.name}' (ID: {workspace.id}) from 'basic' to 'trial'")
                    workspace.subscription_tier = 'trial'
                    updated_count += 1
                else:
                    print(f"Skipping workspace '{workspace.name}' (ID: {workspace.id}) - has paid status: {workspace.subscription_status}")
            
            # Commit the changes
            if updated_count > 0:
                db.session.commit()
                print(f"\n✅ Successfully updated {updated_count} workspaces")
            else:
                print("\n✅ No workspaces needed updating")
                
        except Exception as e:
            print(f"❌ Error updating workspaces: {str(e)}")
            db.session.rollback()
            return False
            
    return True

if __name__ == "__main__":
    print("🔧 Fixing subscription tier display issue...")
    print("=" * 50)
    
    success = fix_subscription_tiers()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Trial users should now see 'Free Trial' instead of 'Starter Plan'")
        print("3. Delete this script file if no longer needed")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)
