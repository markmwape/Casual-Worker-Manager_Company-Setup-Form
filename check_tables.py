#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_init import app, db
from sqlalchemy import text

# Use application context
with app.app_context():
    # Check what tables exist
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
        tables = [r[0] for r in result]
        print('Existing tables:')
        for table in sorted(tables):
            print(f"  - {table}")
        
        # Check company table specifically
        if 'company' in tables:
            print("\nCompany table columns:")
            result = conn.execute(text("PRAGMA table_info(company);")).fetchall()
            for r in result:
                print(f"  - {r[1]} ({r[2]})")
        else:
            print("\n❌ Company table does not exist")
        
        # Check workspace table
        if 'workspace' in tables:
            print("\nWorkspace table columns:")
            result = conn.execute(text("PRAGMA table_info(workspace);")).fetchall()
            for r in result:
                print(f"  - {r[1]} ({r[2]})")
        else:
            print("\n❌ Workspace table does not exist")
