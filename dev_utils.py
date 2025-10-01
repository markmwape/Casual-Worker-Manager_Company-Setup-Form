#!/usr/bin/env python3
"""
Development Utility Script for Embee Accounting - Casual Worker Manager
Provides useful commands for development, testing, and maintenance
"""

import os
import sys
import subprocess
import json
from datetime import datetime

class DevUtils:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
    def run_command(self, command, description=""):
        """Run a shell command and return the result"""
        if description:
            print(f"📋 {description}")
        print(f"🔧 Running: {command}")
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=self.base_dir)
            if result.returncode == 0:
                print("✅ Success")
                if result.stdout.strip():
                    print(f"Output: {result.stdout.strip()}")
                return True
            else:
                print("❌ Failed")
                if result.stderr.strip():
                    print(f"Error: {result.stderr.strip()}")
                return False
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
    
    def check_dependencies(self):
        """Check if all dependencies are installed"""
        print("🔍 Checking Dependencies")
        print("=" * 50)
        
        # Check Python
        python_version = sys.version.split()[0]
        print(f"Python Version: {python_version}")
        
        # Check pip packages
        try:
            import flask
            print(f"✅ Flask: {flask.__version__}")
        except ImportError:
            print("❌ Flask: Not installed")
        
        try:
            import sqlalchemy
            print(f"✅ SQLAlchemy: {sqlalchemy.__version__}")
        except ImportError:
            print("❌ SQLAlchemy: Not installed")
        
        try:
            import stripe
            print(f"✅ Stripe: {getattr(stripe, '__version__', 'installed')}")
        except ImportError:
            print("❌ Stripe: Not installed")
        
        try:
            import pandas
            print(f"✅ Pandas: {pandas.__version__}")
        except ImportError:
            print("❌ Pandas: Not installed")
        
        print()
    
    def setup_development(self):
        """Set up development environment"""
        print("🚀 Setting Up Development Environment")
        print("=" * 50)
        
        # Install dependencies
        if self.run_command("pip install -r requirements.txt", "Installing Python dependencies"):
            print("✅ Dependencies installed successfully")
        else:
            print("❌ Failed to install dependencies")
            return False
        
        # Initialize database
        if self.run_command('python -c "from app_init import app, db; db.create_all(); print(\'Database initialized\')"', 
                          "Initializing database"):
            print("✅ Database initialized successfully")
        else:
            print("❌ Failed to initialize database")
            return False
        
        print("🎉 Development environment setup complete!")
        return True
    
    def run_tests(self):
        """Run the test suite"""
        print("🧪 Running Test Suite")
        print("=" * 50)
        
        # Run API tests
        if self.run_command("python test_api.py", "Running API tests"):
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed")
            return False
    
    def start_development_server(self):
        """Start the development server"""
        print("🌐 Starting Development Server")
        print("=" * 50)
        
        print("Server will start on http://127.0.0.1:5001")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        try:
            subprocess.run(["python", "main.py"], cwd=self.base_dir)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
    
    def create_sample_data(self):
        """Create sample data for testing"""
        print("📊 Creating Sample Data")
        print("=" * 50)
        
        create_sample_script = '''
from app_init import app, db
from models import *
from datetime import datetime, timedelta
import secrets
import string

with app.app_context():
    # Create a sample workspace
    workspace = Workspace(
        name="Sample Company Ltd",
        country="United States",
        industry_type="Technology",
        company_phone="+1234567890",
        company_email="sample@company.com",
        expected_workers_string="below_100",
        created_by=1
    )
    db.session.add(workspace)
    db.session.flush()
    
    # Create a sample company
    company = Company(
        name="Sample Company Ltd",
        registration_number="SC123456",
        address="123 Sample Street, Sample City",
        industry="Technology",
        phone="+1234567890",
        workspace_id=workspace.id,
        created_by=1
    )
    db.session.add(company)
    db.session.flush()
    
    # Create sample workers
    workers = [
        Worker(first_name="John", last_name="Doe", company_id=company.id),
        Worker(first_name="Jane", last_name="Smith", company_id=company.id),
        Worker(first_name="Mike", last_name="Johnson", company_id=company.id),
    ]
    for worker in workers:
        db.session.add(worker)
    
    # Create sample tasks
    tasks = [
        Task(
            name="Construction Project A",
            description="Building construction work",
            start_date=datetime.utcnow(),
            company_id=company.id,
            status="In Progress",
            payment_type="per_day",
            per_day_payout=75.0,
            per_day_currency="USD"
        ),
        Task(
            name="Packaging Task",
            description="Product packaging work",
            start_date=datetime.utcnow(),
            company_id=company.id,
            status="Pending",
            payment_type="per_part",
            per_part_payout=2.5,
            per_part_currency="USD"
        )
    ]
    for task in tasks:
        db.session.add(task)
    
    db.session.commit()
    print(f"✅ Sample data created!")
    print(f"Workspace Code: {workspace.workspace_code}")
    print(f"Workers created: {len(workers)}")
    print(f"Tasks created: {len(tasks)}")
'''
        
        if self.run_command(f'python -c "{create_sample_script}"', "Creating sample data"):
            print("✅ Sample data created successfully")
            return True
        else:
            print("❌ Failed to create sample data")
            return False
    
    def clean_database(self):
        """Clean the database (for development only)"""
        print("🧹 Cleaning Database")
        print("=" * 50)
        
        confirm = input("⚠️  This will delete ALL data. Are you sure? (type 'yes' to confirm): ")
        if confirm.lower() != 'yes':
            print("❌ Operation cancelled")
            return False
        
        clean_script = '''
from app_init import app, db
with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Database cleaned and recreated")
'''
        
        if self.run_command(f'python -c "{clean_script}"', "Cleaning database"):
            print("✅ Database cleaned successfully")
            return True
        else:
            print("❌ Failed to clean database")
            return False
    
    def show_database_info(self):
        """Show database information"""
        print("📊 Database Information")
        print("=" * 50)
        
        info_script = '''
from app_init import app, db
from models import *

with app.app_context():
    print(f"Workspaces: {Workspace.query.count()}")
    print(f"Companies: {Company.query.count()}")
    print(f"Users: {User.query.count()}")
    print(f"Workers: {Worker.query.count()}")
    print(f"Tasks: {Task.query.count()}")
    print(f"Attendance records: {Attendance.query.count()}")
    
    print("\\nSample workspaces:")
    for ws in Workspace.query.limit(5).all():
        print(f"  {ws.name} ({ws.workspace_code})")
'''
        
        self.run_command(f'python -c "{info_script}"', "Getting database information")
    
    def show_help(self):
        """Show available commands"""
        print("🛠️  Embee Accounting Development Utilities")
        print("=" * 50)
        print("Available commands:")
        print("  setup       - Set up development environment")
        print("  deps        - Check dependencies")
        print("  test        - Run test suite")
        print("  server      - Start development server")
        print("  sample      - Create sample data")
        print("  dbinfo      - Show database information")
        print("  clean       - Clean database (DANGEROUS)")
        print("  help        - Show this help message")
        print()
        print("Usage: python dev_utils.py <command>")
        print("Example: python dev_utils.py setup")

def main():
    """Main function"""
    utils = DevUtils()
    
    if len(sys.argv) < 2:
        utils.show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        utils.setup_development()
    elif command == "deps":
        utils.check_dependencies()
    elif command == "test":
        utils.run_tests()
    elif command == "server":
        utils.start_development_server()
    elif command == "sample":
        utils.create_sample_data()
    elif command == "dbinfo":
        utils.show_database_info()
    elif command == "clean":
        utils.clean_database()
    elif command == "help":
        utils.show_help()
    else:
        print(f"❌ Unknown command: {command}")
        utils.show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
