#!/usr/bin/env python3
"""
Test adding a per_hour report field to debug the issue
"""
import sys
import json

try:
    from load_secrets import ensure_secrets_loaded
    ensure_secrets_loaded()
except:
    pass

from app_init import app
from models import db, ReportField, Company, Workspace
from flask import session

def test_add_per_hour_field():
    """Test adding a per_hour report field"""
    with app.app_context():
        # Get first company
        company = Company.query.first()
        if not company:
            print("❌ No company found in database")
            return False
        
        print(f"✓ Found company: {company.name} (ID: {company.id})")
        
        # Try to create a test field
        test_data = {
            'name': 'test_per_hour_field',
            'formula': '90000',
            'field_type': 'numeric',
            'max_limit': None,
            'payout_type': 'per_hour'
        }
        
        print(f"\nTrying to create field with data:")
        print(json.dumps(test_data, indent=2))
        
        try:
            # Check for duplicates
            existing = ReportField.query.filter(
                db.func.lower(ReportField.name) == test_data['name'].lower(),
                ReportField.company_id == company.id
            ).first()
            
            if existing:
                print(f"⚠  Field already exists: {existing.name} (ID: {existing.id})")
                # Delete it for testing
                db.session.delete(existing)
                db.session.commit()
                print("✓ Deleted existing field")
            
            # Create new field
            new_field = ReportField(
                company_id=company.id,
                name=test_data['name'],
                field_type=test_data['field_type'],
                formula=test_data['formula'],
                max_limit=test_data.get('max_limit'),
                payout_type=test_data.get('payout_type', 'per_day')
            )
            
            db.session.add(new_field)
            db.session.commit()
            
            print(f"\n✓ Successfully created field:")
            print(f"  ID: {new_field.id}")
            print(f"  Name: {new_field.name}")
            print(f"  Formula: {new_field.formula}")
            print(f"  Payout Type: {new_field.payout_type}")
            print(f"  Max Limit: {new_field.max_limit}")
            
            # Verify it was saved
            saved_field = ReportField.query.get(new_field.id)
            if saved_field:
                print(f"\n✓ Field verified in database")
                return True
            else:
                print(f"\n❌ Field not found after save")
                return False
                
        except Exception as e:
            print(f"\n❌ Error creating field: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("Testing Per Hour Report Field Creation")
    print("=" * 50)
    
    if test_add_per_hour_field():
        print("\n✓ Test passed!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
