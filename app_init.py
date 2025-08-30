from flask import Flask, session, request, send_from_directory, g, url_for, redirect, jsonify
import logging
import os
import traceback
import subprocess
from datetime import datetime
from models import db, User, Company, Workspace, UserWorkspace

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

# Initialize database with Alembic migrations
with app.app_context():
    try:
        # Run basic table creation for Cloud SQL
        if os.environ.get('K_SERVICE'):  # In Cloud Run
            logging.info("Cloud Run environment detected - running basic table creation")
            try:
                import psycopg2
                from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
                
                # Get connection details
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
                
                # Create user table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS "user" (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(150) UNIQUE NOT NULL,
                        profile_picture TEXT,
                        role VARCHAR(50) DEFAULT 'User',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                # Ensure system user exists for workspace creation
                cur.execute("""
                    INSERT INTO "user" (email, profile_picture, role)
                    SELECT 'system@workspace.com', '', 'System'
                    WHERE NOT EXISTS (
                        SELECT 1 FROM "user" WHERE email='system@workspace.com'
                    );
                """)
                
                # Create workspace table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS workspace (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        workspace_code VARCHAR(16) UNIQUE NOT NULL,
                        address TEXT,
                        country VARCHAR(100) NOT NULL,
                        industry_type VARCHAR(100) NOT NULL,
                        company_phone VARCHAR(20) NOT NULL,
                        company_email VARCHAR(150) NOT NULL,
                        expected_workers INTEGER,
                        expected_workers_string VARCHAR(50) NOT NULL DEFAULT 'below_100',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by INTEGER NOT NULL,
                        stripe_customer_id VARCHAR(255),
                        stripe_subscription_id VARCHAR(255),
                        subscription_status VARCHAR(50) DEFAULT 'trial',
                        trial_end_date TIMESTAMP,
                        subscription_end_date TIMESTAMP,
                        FOREIGN KEY (created_by) REFERENCES "user"(id)
                    );
                """)
                
                # Create user_workspace table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_workspace (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        workspace_id INTEGER NOT NULL,
                        role VARCHAR(50) NOT NULL DEFAULT 'User',
                        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES "user"(id),
                        FOREIGN KEY (workspace_id) REFERENCES workspace(id),
                        UNIQUE(user_id, workspace_id)
                    );
                """)
                # Create company table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS company (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        registration_number VARCHAR(100) NOT NULL,
                        address TEXT NOT NULL,
                        industry VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by INTEGER NOT NULL REFERENCES "user"(id),
                        workspace_id INTEGER NOT NULL REFERENCES workspace(id),
                        daily_payout_rate FLOAT DEFAULT 56.0 NOT NULL,
                        currency VARCHAR(3) DEFAULT 'ZMW' NOT NULL,
                        currency_symbol VARCHAR(5) DEFAULT 'K' NOT NULL,
                        phone VARCHAR(20) NOT NULL
                    );
                """)
                
                # Create worker table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS worker (
                        id SERIAL PRIMARY KEY,
                        first_name VARCHAR(100),
                        last_name VARCHAR(100),
                        date_of_birth DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        company_id INTEGER NOT NULL REFERENCES company(id),
                        user_id INTEGER REFERENCES "user"(id)
                    );
                """)
                
                # Create task table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS task (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        status VARCHAR(50) DEFAULT 'Pending',
                        start_date TIMESTAMP NOT NULL,
                        completion_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        company_id INTEGER NOT NULL REFERENCES company(id),
                        payment_type VARCHAR(20) NOT NULL DEFAULT 'per_day',
                        per_part_rate FLOAT,
                        per_part_payout FLOAT,
                        per_part_currency VARCHAR(10)
                    );
                """)
                
                # Create attendance table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS attendance (
                        id SERIAL PRIMARY KEY,
                        worker_id INTEGER NOT NULL REFERENCES worker(id),
                        date DATE NOT NULL,
                        check_in_time TIMESTAMP,
                        check_out_time TIMESTAMP,
                        status VARCHAR(50) DEFAULT 'Absent',
                        company_id INTEGER NOT NULL REFERENCES company(id),
                        task_id INTEGER REFERENCES task(id),
                        units_completed FLOAT DEFAULT 0.0
                    );
                """)
                
                # Create task_workers junction table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS task_workers (
                        task_id INTEGER NOT NULL REFERENCES task(id),
                        worker_id INTEGER NOT NULL REFERENCES worker(id),
                        PRIMARY KEY (task_id, worker_id)
                    );
                """)
                
                # Create master_admin table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS master_admin (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(150) UNIQUE NOT NULL,
                        name VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by INTEGER REFERENCES master_admin(id),
                        is_active BOOLEAN DEFAULT TRUE
                    );
                """)
                
                # Create report_field table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS report_field (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        field_type VARCHAR(50) NOT NULL,
                        is_nullable BOOLEAN DEFAULT TRUE,
                        max_limit INTEGER,
                        payout_type VARCHAR(20) DEFAULT 'fixed'
                    );
                """)
                
                # Create import_field table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS import_field (
                        id SERIAL PRIMARY KEY,
                        company_id INTEGER NOT NULL REFERENCES company(id),
                        name VARCHAR(100) NOT NULL,
                        field_type VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Create worker_custom_field_value table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS worker_custom_field_value (
                        id SERIAL PRIMARY KEY,
                        worker_id INTEGER NOT NULL REFERENCES worker(id),
                        custom_field_id INTEGER NOT NULL REFERENCES import_field(id),
                        value VARCHAR(255)
                    );
                """)
                
                # Create worker_import_log table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS worker_import_log (
                        id SERIAL PRIMARY KEY,
                        filename VARCHAR(255) NOT NULL,
                        imported_count INTEGER NOT NULL,
                        failed_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        company_id INTEGER NOT NULL REFERENCES company(id)
                    );
                """)
                
                cur.close()
                conn.close()
                logging.info("Core tables created successfully in Cloud SQL")
                
            except Exception as db_error:
                logging.error(f"Error creating tables in Cloud SQL: {db_error}")
        else:
            # Local development - use Alembic
            result = subprocess.run(
                ["python3", "-m", "alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                timeout=30
            )
            if result.returncode == 0:
                logging.info("Alembic migrations applied successfully")
            else:
                logging.warning(f"Alembic migration warning: {result.stderr}")
    except subprocess.TimeoutExpired:
        logging.warning("Alembic migration timed out, continuing with application startup")
    except Exception as e:
        logging.error(f"Error applying migrations: {str(e)}")
        # Continue execution even if migration fails
    
    # Skip schema verification for production - rely on Alembic migrations
    if not (os.environ.get('GAE_ENV', '').startswith('standard') or os.environ.get('INSTANCE_CONNECTION_NAME') or os.environ.get('K_SERVICE')):
        # Only do schema verification for local SQLite development
        try:
            with db.engine.connect() as conn:
                # Check and add workspace_id to company table
                cursor = conn.execute(db.text("PRAGMA table_info(company)"))
                company_columns = [row[1] for row in cursor.fetchall()]
                
                if 'workspace_id' not in company_columns:
                    logging.info("Adding workspace_id column to company table")
                    conn.execute(db.text("ALTER TABLE company ADD COLUMN workspace_id INTEGER REFERENCES workspace(id)"))
                    conn.commit()
                
                # Other column checks for SQLite...
            
            logging.info("Local database schema verification completed successfully")
            
        except Exception as e:
            logging.error(f"Error ensuring local database schema: {str(e)}")
    else:
        logging.info("Production environment detected - skipping schema verification, relying on Alembic migrations")

app.config['LOGO_URL'] = '/static/logo.png'

# Set default theme
app.config['THEME'] = 'lofi'
# PICK FROM ANY DAISY UI THEME ALL YOU HAVE TO DO IS CHANGE THIS VARIABLE!

# Set default app title
app.config['APP_TITLE'] = 'My Dashboard'

# Context processor to inject theme and app title into all templates
@app.context_processor
def inject_theme_and_title():
    return dict(theme=app.config['THEME'], app_title=app.config['APP_TITLE'])

# Set up authentication for protected routes
protected_routes = [
    'home_route', 
    'workers_route', 
    'tasks_route', 
    'reports_route', 
    'attendance_route',
    'task_attendance_route',
    'task_units_completed_route',
    'payments_route',
    'update_payout_rate',
    'create_worker',
    'create_task',
    'create_company',
    'import_field',
    'delete_import_field',
    'import_workers',
    'add_team_member',
    'update_team_member_role',
    'delete_team_member',
    'analyze_columns',
    'import_mapped_workers',
    'delete_worker',
    'update_worker',
    'update_task_attendance',
    'add_worker_to_task',
    'bulk_delete_workers',
    'update_task_date',
    'delete_task',
    'update_task_status',
    'download_report',
    'manage_report_field'
]

# Create a simple before_request handler that bypasses auth for now
@app.before_request
def check_auth():
    # Only check authentication for protected routes, not for sign-in related routes
    if request.endpoint and request.endpoint != 'static':
        # Check if this is a protected route that needs authentication
        if request.endpoint in protected_routes:
            # Add debugging
            logging.info(f"Checking auth for endpoint: {request.endpoint}")
            logging.info(f"Session user: {session.get('user')}")
            logging.info(f"Session keys: {list(session.keys())}")
            
            # For protected routes, check if user is authenticated
            if 'user' not in session or 'user_email' not in session['user']:
                logging.warning(f"Authentication failed for {request.endpoint}. Session: {dict(session)}")
                # Redirect to workspace selection instead of signin
                return redirect(url_for('workspace_selection_route'))
            
            # Check if user has an active workspace
            if 'current_workspace' not in session:
                logging.warning(f"No active workspace for {request.endpoint}. Session: {dict(session)}")
                return redirect(url_for('workspace_selection_route'))
            
            # Ensure demo user exists in DB for authenticated users
            try:
                user = User.query.filter_by(email=session['user']['user_email']).first()
                if not user:
                    user = User(email=session['user']['user_email'], profile_picture='', role='Admin')
                    db.session.add(user)
                    db.session.commit()
                    logging.info("Created user in DB.")
            except Exception as e:
                logging.error(f"Error creating/querying user: {str(e)}")
                # Continue without user creation if there's a database error
            
            # Check trial expiration for admin users
            try:
                if user and 'current_workspace' in session:
                    workspace_id = session['current_workspace']['id']
                    workspace = Workspace.query.get(workspace_id)
                    
                    if workspace and session['current_workspace'].get('role') == 'Admin':
                        from datetime import datetime
                        now = datetime.utcnow()
                        
                        # Check if trial has expired
                        if workspace.trial_end_date and now > workspace.trial_end_date and workspace.subscription_status == 'trial':
                            # Only redirect to payments if not already on payments page
                            if request.endpoint != 'payments_route':
                                logging.info(f"Trial expired for workspace {workspace.name}, redirecting admin to payments")
                                return redirect(url_for('payments_route'))
            except Exception as e:
                logging.error(f"Error checking trial expiration: {str(e)}")
            
            # Ensure demo company exists in DB for authenticated users
            try:
                if user and 'current_workspace' in session:
                    workspace_id = session['current_workspace']['id']
                    company = Company.query.filter_by(workspace_id=workspace_id).first()
                    if not company:
                        company = Company(
                            name='Demo Company',
                            registration_number='DEMO123',
                            address='123 Demo Street',
                            industry='Demo Industry',
                            created_by=user.id,
                            workspace_id=workspace_id,
                            daily_payout_rate=56.0,
                            currency='ZMW',
                            currency_symbol='K',
                            phone='0000000000'  # Default phone value
                        )
                        db.session.add(company)
                        db.session.commit()
                        logging.info("Created demo company in DB.")
            except Exception as e:
                logging.error(f"Error creating demo company: {str(e)}")

# Add a test route to verify authentication bypass
@app.route("/test-auth")
def test_auth():
    return jsonify({
        'user': session.get('user'),
        'current_workspace': session.get('current_workspace'),
        'message': 'Authentication bypass working!'
    })

@app.route("/debug")
def debug_info():
    """Debug endpoint to check environment and database configuration"""
    return jsonify({
        'environment_variables': {
            'INSTANCE_CONNECTION_NAME': os.environ.get('INSTANCE_CONNECTION_NAME'),
            'DB_USER': os.environ.get('DB_USER'),
            'DB_NAME': os.environ.get('DB_NAME'),
            'DB_HOST': os.environ.get('DB_HOST'),
            'GAE_ENV': os.environ.get('GAE_ENV')
        },
        'database_uri': app.config['SQLALCHEMY_DATABASE_URI'],
        'using_cloud_sql': 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'],
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route("/test-reports")
def test_reports():
    return jsonify({
        'message': 'Reports route is accessible!',
        'session': dict(session)
    })

@app.route("/health")
def health_check():
    """Health check endpoint for Cloud Run"""
    try:
        # Log environment variables for debugging
        logging.info(f"Health check - Environment variables:")
        logging.info(f"  INSTANCE_CONNECTION_NAME: {os.environ.get('INSTANCE_CONNECTION_NAME')}")
        logging.info(f"  DB_USER: {os.environ.get('DB_USER')}")
        logging.info(f"  DB_NAME: {os.environ.get('DB_NAME')}")
        logging.info(f"  K_SERVICE: {os.environ.get('K_SERVICE')}")
        logging.info(f"  GAE_ENV: {os.environ.get('GAE_ENV')}")
        logging.info(f"  Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Test database connection
        with app.app_context():
            logging.info("Testing database connection...")
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT 1"))
                logging.info(f"Database connection successful: {result.fetchone()}")
            
            # Run Alembic migrations if needed
            logging.info("Running Alembic migrations...")
            try:
                result = subprocess.run(
                    ["python3", "-m", "alembic", "upgrade", "head"],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                    timeout=60
                )
                if result.returncode != 0:
                    logging.warning(f"Alembic migration warning: {result.stderr}")
                    logging.warning(f"Alembic migration stdout: {result.stdout}")
                else:
                    logging.info("Alembic migrations applied successfully")
            except Exception as e:
                logging.warning(f"Could not run Alembic migrations: {e}")
                # Continue without failing the health check
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'migrations': 'applied',
            'environment': {
                'instance_connection_name': os.environ.get('INSTANCE_CONNECTION_NAME'),
                'db_user': os.environ.get('DB_USER'),
                'db_name': os.environ.get('DB_NAME'),
                'k_service': os.environ.get('K_SERVICE'),
                'gae_env': os.environ.get('GAE_ENV')
            },
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        logging.error(f"Exception type: {type(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'error_type': str(type(e)),
            'environment': {
                'instance_connection_name': os.environ.get('INSTANCE_CONNECTION_NAME'),
                'db_user': os.environ.get('DB_USER'),
                'db_name': os.environ.get('DB_NAME'),
                'k_service': os.environ.get('K_SERVICE'),
                'gae_env': os.environ.get('GAE_ENV')
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 500

