#!/usr/bin/env python3
"""
Test script to verify that date_of_birth field is working correctly
"""

from app_init import app, db
from models import Worker, Company, Workspace, User
from datetime import datetime, date

def test_date_of_birth():
    with app.app_context():
        print("Testing date_of_birth field...")
        
        # Get a test worker if any exist
        worker = Worker.query.first()
        
        if worker:
            print(f"Found worker: {worker.first_name} {worker.last_name}")
            print(f"Current date_of_birth: {worker.date_of_birth}")
            
            # Update with a test date
            test_date = date(1990, 5, 15)
            worker.date_of_birth = test_date
            db.session.commit()
            
            print(f"Updated date_of_birth to: {worker.date_of_birth}")
            
            # Verify the update
            updated_worker = Worker.query.get(worker.id)
            print(f"Verified date_of_birth: {updated_worker.date_of_birth}")
            
        else:
            print("No workers found in database")
            
        print("Test completed!")

if __name__ == '__main__':
    test_date_of_birth()
