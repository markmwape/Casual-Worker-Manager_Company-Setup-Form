from flask import Flask, session, request, send_from_directory, g, url_for, redirect, jsonify
import logging
import os
import traceback
import subprocess
from datetime import datetime
from models import db, User, Company, Workspace, UserWorkspace

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, environment variables should be set externally
    pass

# Create Flask app
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Database configuration - use Cloud SQL in production, SQLite for local development
if os.environ.get('GAE_ENV', '').startswith('standard') or os.environ.get('INSTANCE_CONNECTION_NAME') or os.environ.get('K_SERVICE'):
    # Production: Use Cloud SQL
    db_user = os.environ.get('DB_USER', 'postgres')
    db_pass = os.environ.get('DB_PASS', '')
    db_name = os.environ.get('DB_NAME', 'casual_worker_db')
    
    # For Cloud SQL Proxy
    if os.environ.get('INSTANCE_CONNECTION_NAME'):
        # Use the Cloud SQL connection format
        connection_name = os.environ.get('INSTANCE_CONNECTION_NAME')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{connection_name}'
    else:
        db_host = os.environ.get('DB_HOST', 'localhost')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}'
    
    # Log database configuration for debugging
    logging.info(f"Using Cloud SQL configuration:")
    logging.info(f"  DB_USER: {db_user}")
    logging.info(f"  DB_NAME: {db_name}")
    logging.info(f"  INSTANCE_CONNECTION_NAME: {os.environ.get('INSTANCE_CONNECTION_NAME')}")
    logging.info(f"  K_SERVICE: {os.environ.get('K_SERVICE')}")
    logging.info(f"  GAE_ENV: {os.environ.get('GAE_ENV')}")
    logging.info(f"  Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
else:
    # Development: Use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
    logging.info("Using SQLite configuration for development")
    logging.info(f"  Environment variables:")
    logging.info(f"    INSTANCE_CONNECTION_NAME: {os.environ.get('INSTANCE_CONNECTION_NAME')}")
    logging.info(f"    K_SERVICE: {os.environ.get('K_SERVICE')}")
    logging.info(f"    GAE_ENV: {os.environ.get('GAE_ENV')}")

app.static_folder = 'static'
app.static_url_path = '/static'

# Configure session settings for production
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Initialize extensions
db.init_app(app)

# Master Admin Configuration
MASTER_ADMIN_EMAIL = os.environ.get('MASTER_ADMIN_EMAIL', 'markbmwape@gmail.com')  # Set your email here

def is_master_admin():
    """Check if current user is the master admin"""
    if 'user' not in session or 'user_email' not in session['user']:
        return False
    
    # Check against MasterAdmin table first
    from models import MasterAdmin
    master_admin = MasterAdmin.query.filter_by(
        email=session['user']['user_email'], 
        is_active=True
    ).first()
    
    if master_admin:
        return True
    
    # Fallback to hardcoded email for backward compatibility
    return session['user']['user_email'] == MASTER_ADMIN_EMAIL

def master_admin_required(f):
    """Decorator to require master admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_master_admin():
            return redirect(url_for('home_route'))
        return f(*args, **kwargs)
    return decorated_function

# Import routes to register them with the app early
import routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def auth_required(protected_routes=[]):
    def decorator(f):
        def decorated_view(*args, **kwargs):
            if request.endpoint not in protected_routes or request.endpoint == 'static':
                return f(*args, **kwargs)
            
            # For now, bypass authentication and create a mock user session
            if 'user' not in session or 'user_email' not in session['user']:
                # Create a mock user session
                session['user'] = {
                    'user_email': 'demo@example.com',
                    'display_name': 'Demo User',
                    'photo_url': '',
                    'uid': 'demo123'
                }
            
            return f(*args, **kwargs)
        decorated_view.__name__ = f.__name__
        return decorated_view
    return decorator

@app.after_request
def create_or_update_user(response):
    try:
        if 'user' in session and 'user_email' in session['user']:
            email = session['user']['user_email']
            profile_picture = session['user'].get('photo_url')
            with app.app_context():
                user = User.query.filter_by(email=email).first()
                if not user:
                    new_user = User(email=email, profile_picture=profile_picture)
                    db.session.add(new_user)
                    db.session.commit()
                    logging.info(f"Created new user: {email}")
                elif user.profile_picture != profile_picture:
                    user.profile_picture = profile_picture
                    db.session.commit()
                    logging.info(f"Updated profile picture for user: {email}")
    except Exception as e:
        logging.error(f"Error in create_or_update_user: {str(e)}")
        # Don't let database errors break the response
    return response

# Initialize database with Alembic migrations if enabled
if os.environ.get('RUN_MIGRATIONS_AT_STARTUP', 'false').lower() == 'true':
    with app.app_context():
        try:
            # Run basic table creation for Cloud SQL
            if os.environ.get('K_SERVICE'):
                logging.info("Cloud Run startup migrations enabled - running basic table creation")
                import psycopg2
                from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
                # Connection details
                db_user = os.environ.get('DB_USER', 'cwuser')
                db_pass = os.environ.get('DB_PASS', '')
                db_name = os.environ.get('DB_NAME', 'cw_manager')
                connection_name = os.environ.get('INSTANCE_CONNECTION_NAME', '')
                # Connect and create tables
                conn = psycopg2.connect(
                    dbname=db_name,
                    user=db_user,
                    password=db_pass,
                    host=f"/cloudsql/{connection_name}"
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cur = conn.cursor()
                # Create user table if not exists
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS \"user\" (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(150) UNIQUE NOT NULL,
                        profile_picture TEXT,
                        role VARCHAR(50) DEFAULT 'User',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                # Ensure master admin user exists
                cur.execute("""
                    INSERT INTO master_admin (email, name, is_active, created_at)
                    SELECT 'markbmwape@gmail.com', 'Mark Mwape', TRUE, CURRENT_TIMESTAMP
                    WHERE NOT EXISTS (
                        SELECT 1 FROM master_admin WHERE email='markbmwape@gmail.com'
                    );
                """)
        except Exception as e:
            logging.error(f"Startup migrations error: {str(e)}")

