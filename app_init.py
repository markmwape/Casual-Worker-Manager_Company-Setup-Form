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

# Load secrets from Google Secret Manager if in production
try:
    from load_secrets import ensure_secrets_loaded
    ensure_secrets_loaded()
except ImportError as e:
    logging.warning(f"Could not import secret loading functionality: {e}")
except Exception as e:
    logging.warning(f"Error loading secrets: {e}")

# Create Flask app
app = Flask(__name__)

secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    logging.warning("SECRET_KEY not set; using default insecure key")
    secret_key = 'supersecretkey'
app.secret_key = secret_key

# Database configuration - use Cloud SQL in production (App Engine or explicit Cloud SQL), SQLite for local development or when no DB config
if os.environ.get('GAE_ENV', '').startswith('standard') or os.environ.get('INSTANCE_CONNECTION_NAME'):
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

# Initialize database tables with better error handling
def init_database_safely():
    """Initialize database with comprehensive error handling"""
    try:
        with app.app_context():
            # Create all tables that don't exist
            db.create_all()
            logging.info("✅ Database tables created successfully")
            
            # Add missing columns if needed
            from sqlalchemy import text
            columns_to_add = [
                ("subscription_tier", "VARCHAR(50)", "free"),
                ("subscription_status", "VARCHAR(50)", "active"), 
                ("trial_end_date", "DATETIME", None),
                ("stripe_customer_id", "VARCHAR(255)", None),
                ("stripe_subscription_id", "VARCHAR(255)", None)
            ]
            
            for column_name, column_type, default_value in columns_to_add:
                try:
                    if default_value:
                        sql = f"ALTER TABLE workspace ADD COLUMN IF NOT EXISTS {column_name} {column_type} DEFAULT '{default_value}'"
                    else:
                        sql = f"ALTER TABLE workspace ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
                    
                    db.session.execute(text(sql))
                    logging.info(f"✅ Added column {column_name} to workspace table")
                except Exception as col_error:
                    logging.info(f"Column {column_name} already exists or couldn't be added: {str(col_error)}")
                    continue
            
            try:
                db.session.commit()
                logging.info("✅ Database schema updated successfully")
            except Exception as commit_error:
                db.session.rollback()
                logging.warning(f"Database commit failed, rolling back: {str(commit_error)}")

            # Automatically apply Alembic migrations
            try:
                from alembic.config import Config
                from alembic import command
                alembic_cfg = Config(os.path.join(os.getcwd(), 'alembic.ini'))
                command.upgrade(alembic_cfg, 'head')
                logging.info("✅ Alembic migrations applied successfully")
            except Exception as alembic_error:
                logging.error(f"❌ Failed to apply Alembic migrations: {alembic_error}")
                logging.error(traceback.format_exc())
    except Exception as e:
        logging.error(f"❌ Database initialization failed: {e}")
        logging.error("App will continue without database initialization")

# Call database initialization
try:
    init_database_safely()
except Exception as e:
    logging.error(f"Database initialization wrapper failed: {e}")
    # Continue anyway - app can still work with manual database setup

# Master Admin Configuration
MASTER_ADMIN_EMAIL = os.environ.get('MASTER_ADMIN_EMAIL')
# Enforce master admin email only in production (non-SQLite) environments
db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
if 'sqlite' not in db_uri:
    if not MASTER_ADMIN_EMAIL:
        logging.error("MASTER_ADMIN_EMAIL environment variable not set in production environment")
        raise RuntimeError("MASTER_ADMIN_EMAIL must be set in environment for security")
else:
    if not MASTER_ADMIN_EMAIL:
        logging.warning("MASTER_ADMIN_EMAIL not set; skipping master admin checks in development")

def is_master_admin():
    """Check if current user is the master admin"""
    if 'user' not in session or 'user_email' not in session['user']:
        return False
    
    try:
        # Check against MasterAdmin table first
        from models import MasterAdmin
        master_admin = MasterAdmin.query.filter_by(
            email=session['user']['user_email'], 
            is_active=True
        ).first()
        
        if master_admin:
            return True
    except Exception as e:
        # Table might not exist yet, fall back to hardcoded check
        logging.warning(f"Could not query MasterAdmin table: {str(e)}")
    
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

