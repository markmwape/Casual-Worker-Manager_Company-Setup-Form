#!/usr/bin/env python3
"""
Test script to verify database connectivity and migrations
"""
import os
import sys
import sqlite3
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_init import app
from models import db, User
from abilities import apply_sqlite_migrations

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database():
    """Test database connectivity and migrations"""
    try:
        with app.app_context():
            # Test database connection
            logger.info("Testing database connection...")
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))
            logger.info("✓ Database connection successful")
            
            # Apply migrations
            logger.info("Applying migrations...")
            apply_sqlite_migrations(db.engine, db.Model, 'migrations')
            logger.info("✓ Migrations applied successfully")
            
            # Test User model
            logger.info("Testing User model...")
            users = User.query.all()
            logger.info(f"✓ Found {len(users)} users in database")
            
            # Test creating a user
            test_user = User.query.filter_by(email='test@example.com').first()
            if not test_user:
                test_user = User(email='test@example.com', role='Admin')
                db.session.add(test_user)
                db.session.commit()
                logger.info("✓ Created test user successfully")
            else:
                logger.info("✓ Test user already exists")
            
            # Test querying user with role
            user_with_role = User.query.filter_by(email='test@example.com').first()
            if user_with_role and hasattr(user_with_role, 'role'):
                logger.info(f"✓ User role column exists: {user_with_role.role}")
            else:
                logger.error("✗ User role column missing or not accessible")
                return False
            
            logger.info("✓ All database tests passed!")
            return True
            
    except Exception as e:
        logger.error(f"✗ Database test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1) 