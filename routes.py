from models import WorkerImportLog, ImportField, WorkerCustomFieldValue, ReportField, ActivityLog
from models import Attendance, Task, Worker, Company, User, Workspace, UserWorkspace, MasterAdmin
from flask import render_template, session, redirect, url_for, make_response, abort, request, jsonify, send_file
from app_init import app, db
from datetime import timedelta
from sqlalchemy import and_
import json
from abilities import upload_file_to_storage, download_file_from_storage
import pandas as pd
import logging
import traceback
import os
from datetime import datetime
from sqlalchemy import and_
import io
import re
from app_init import master_admin_required
from sqlalchemy import func, desc
from activity_logger import log_activity, get_recent_activities, get_activity_stats, LogMessages

def get_current_company():
    """Helper function to get the current company from workspace session"""
    if 'current_workspace' not in session:
        return None
    
    workspace_id = session['current_workspace']['id']
    return Company.query.filter_by(workspace_id=workspace_id).first()

def get_current_user():
    """Helper function to get the current user from session"""
    if 'user' not in session or 'user_email' not in session['user']:
        return None
    
    user_email = session['user']['user_email']
    return User.query.filter_by(email=user_email).first()

@app.route('/workspace-selection')
def workspace_selection_route():
    """Route for workspace selection page"""
    return render_template('workspace_selection.html')

@app.route('/api/workspace/join', methods=['POST'])
def join_workspace():
    """API endpoint to join a workspace with a code"""
    try:
        data = request.get_json()
        workspace_code = data.get('workspace_code', '').strip().upper()
        
        if not workspace_code or len(workspace_code) != 16:
            return jsonify({"error": "Invalid workspace code"}), 400
        
        # Find workspace by code
        workspace = Workspace.query.filter_by(workspace_code=workspace_code).first()
        if not workspace:
            return jsonify({"error": "Workspace not found"}), 404
        
        return jsonify({
            "success": True,
            "workspace": {
                "id": workspace.id,
                "name": workspace.name,
                "code": workspace.workspace_code,
                "address": workspace.address
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error joining workspace: {str(e)}")
        return jsonify({"error": "Failed to join workspace"}), 500

@app.route('/api/workspace/create', methods=['POST'])
def create_workspace():
    """API endpoint to create a new workspace"""
    try:
        # Log environment variables for debugging
        logging.info("Environment variables:")
        logging.info(f"  INSTANCE_CONNECTION_NAME: {os.environ.get('INSTANCE_CONNECTION_NAME')}")
        logging.info(f"  DB_USER: {os.environ.get('DB_USER')}")
        logging.info(f"  DB_NAME: {os.environ.get('DB_NAME')}")
        logging.info(f"  K_SERVICE: {os.environ.get('K_SERVICE')}")
        
        # Test database connection with better error handling
        logging.info("Testing database connection before workspace creation")
        try:
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT 1"))
                logging.info(f"Database connection successful: {result.fetchone()}")
        except Exception as db_error:
            logging.error(f"Database connection failed: {str(db_error)}")
            logging.error(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')}")
            # Try to continue anyway - maybe the database will work for actual operations
        
        data = request.get_json()
        logging.info(f"Received workspace creation data: {data}")
        
        company_name = data.get('company_name', '').strip()
        country = data.get('country', '').strip()
        industry_type = data.get('industry_type', '').strip()
        expected_workers = str(data.get('expected_workers', 'not_specified')).strip()
        company_phone = data.get('company_phone', '').strip()
        company_email = data.get('company_email', '').strip()
        
        # Validate all required fields
        required_fields = {
            'company_name': company_name,
            'country': country,
            'industry_type': industry_type,
            'company_phone': company_phone,
            'company_email': company_email
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, company_email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Validate expected workers format (if provided)
        valid_worker_ranges = ['below_100', '100_250', '251_500', '501_1000', 'above_1000', 'not_specified']
        if expected_workers not in valid_worker_ranges:
            expected_workers = 'not_specified'
        
        # Store workspace creation data in session for completion during sign-in
        # No system user needed - workspace will be created when admin signs in
        workspace_data = {
            'company_name': company_name,
            'country': country,
            'industry_type': industry_type,
            'expected_workers_string': expected_workers,
            'company_phone': company_phone,
            'company_email': company_email
        }
        
        # Generate a temporary workspace code for the user to use
        import secrets
        import string
        temp_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        
        # Return the workspace data for frontend to store
        return jsonify({
            "success": True,
            "workspace": {
                "temp_code": temp_code,
                "name": company_name,
                "code": temp_code,
                "country": country,
                "industry_type": industry_type,
                "company_phone": company_phone,
                "company_email": company_email
            },
            "deferred_creation": True
        }), 200
        
    except Exception as e:
        logging.error(f"Error creating workspace: {str(e)}")
        logging.error(f"Exception type: {type(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({"error": "Failed to create workspace"}), 500

@app.route('/set_session', methods=['POST'])
def set_session():
    try:
        user_data = request.json
        logging.info(f"Setting session with user data: {user_data}")
        
        if not user_data:
            logging.error("No user data received")
            return jsonify({"error": "No user data provided"}), 400
        
        # Extract email from user data
        email = user_data.get('email') or user_data.get('user_email')
        if not email:
            logging.error("No email found in user data")
            return jsonify({"error": "No email provided"}), 400
        
        # Get workspace data if available
        workspace_data = user_data.get('workspace_data')
        
        session['user'] = {
            'user_email': email,
            'display_name': user_data.get('displayName', ''),
            'photo_url': user_data.get('photoURL', ''),
            'uid': user_data.get('uid')
        }

        # Create or update user in database
        try:
            with app.app_context():
                user = User.query.filter_by(email=email).first()
                if not user:
                    user = User(email=email, profile_picture=user_data.get('photoURL', ''))
                    db.session.add(user)
                    db.session.commit()
                    logging.info(f"Created new user: {email}")
                
                workspace = None
                user_workspace = None
                
                # Handle workspace assignment if workspace data is provided
                if workspace_data:
                    try:
                        # Check if this is a deferred workspace creation (new workspace)
                        if workspace_data.get('deferred_creation') or workspace_data.get('temp_code'):
                            # Create the workspace now with the actual admin user
                            workspace = Workspace(
                                name=workspace_data.get('company_name') or workspace_data.get('name'),
                                country=workspace_data.get('country', ''),
                                industry_type=workspace_data.get('industry_type', ''),
                                expected_workers_string=workspace_data.get('expected_workers_string', 'not_specified'),
                                expected_workers=0,
                                company_phone=workspace_data.get('company_phone', ''),
                                company_email=workspace_data.get('company_email', ''),
                                address="",
                                created_by=user.id  # Admin user is the creator
                            )
                            
                            db.session.add(workspace)
                            db.session.flush()  # Get the workspace ID
                            
                            # Create a company for this workspace
                            company = Company(
                                name=workspace_data.get('company_name') or workspace_data.get('name'),
                                registration_number="",
                                address="",
                                industry=workspace_data.get('industry_type', ''),
                                phone=workspace_data.get('company_phone', ''),
                                created_by=user.id,
                                workspace_id=workspace.id
                            )
                            db.session.add(company)
                            
                            # Add admin user to workspace
                            user_workspace = UserWorkspace(
                                user_id=user.id,
                                workspace_id=workspace.id,
                                role='Admin'
                            )
                            db.session.add(user_workspace)
                            db.session.commit()
                            
                            # Log workspace creation (with safe activity logging)
                            try:
                                log_activity(
                                    action_type='create',
                                    resource_type='workspace',
                                    description=LogMessages.WORKSPACE_CREATED.format(name=workspace.name),
                                    resource_id=workspace.id,
                                    details={
                                        'workspace_name': workspace.name,
                                        'country': workspace.country,
                                        'industry_type': workspace.industry_type,
                                        'company_phone': workspace.company_phone,
                                        'company_email': workspace.company_email
                                    },
                                    user_email=email,
                                    workspace_id=workspace.id
                                )
                            except Exception as log_error:
                                logging.warning(f"Failed to log workspace creation activity: {log_error}")
                            
                            logging.info(f"Created new workspace {workspace.name} with admin {email}")
                            
                        elif workspace_data.get('id'):
                            # Existing workspace
                            workspace = Workspace.query.get(workspace_data['id'])
                            if workspace:
                                # Check if user is already in this workspace
                                user_workspace = UserWorkspace.query.filter_by(
                                    user_id=user.id, 
                                    workspace_id=workspace.id
                                ).first()
                                
                                logging.info(f"Session setting - User ID: {user.id}, Workspace ID: {workspace.id}, Workspace created_by: {workspace.created_by}")
                                logging.info(f"Session setting - Existing UserWorkspace: {user_workspace.role if user_workspace else 'None'}")
                                
                                if not user_workspace:
                                    # Check if user is the workspace creator (admin)
                                    if workspace.created_by == user.id:
                                        # Workspace creator gets admin access
                                        role = 'Admin'
                                        user_workspace = UserWorkspace(
                                            user_id=user.id,
                                            workspace_id=workspace.id,
                                            role=role
                                        )
                                        db.session.add(user_workspace)
                                        db.session.commit()
                                        logging.info(f"Added workspace creator {email} to workspace {workspace.name} with role {role}")
                                    else:
                                        # For non-creators, check if they have been added as team members
                                        # If not, deny access
                                        logging.warning(f"User {email} attempted to join workspace {workspace.name} but is not a team member")
                                        return jsonify({"error": "You are not authorized to access this workspace. Please contact the workspace administrator to be added as a team member."}), 403
                        else:
                            logging.error("Invalid workspace data provided")
                            return jsonify({"error": "Invalid workspace data"}), 400
                    except Exception as workspace_error:
                        logging.error(f"Error handling workspace data: {workspace_error}")
                        import traceback
                        logging.error(f"Workspace error traceback: {traceback.format_exc()}")
                        # Continue without workspace for now
                        workspace = None
                        user_workspace = None
                
                # If no workspace data provided, just set up basic session without workspace
                if not workspace_data:
                    logging.info(f"No workspace data provided, setting up basic session for {email}")
                
                # Set workspace info in session if we have a workspace
                if workspace:
                    session['current_workspace'] = {
                        'id': workspace.id,
                        'name': workspace.name,
                        'code': workspace.workspace_code,
                        'role': user_workspace.role if user_workspace else 'Admin',
                        'company_email': workspace.company_email,
                        'company_phone': workspace.company_phone
                    }
                    
                    # Log user login to workspace (with safe activity logging)
                    try:
                        log_activity(
                            action_type='login',
                            resource_type='workspace',
                            description=LogMessages.USER_LOGIN,
                            resource_id=workspace.id,
                            details={
                                'workspace_name': workspace.name,
                                'user_role': user_workspace.role if user_workspace else 'Admin'
                            },
                            user_email=email,
                            workspace_id=workspace.id
                        )
                    except Exception as log_error:
                        logging.warning(f"Failed to log user login activity: {log_error}")
                    
                    # Ensure a company exists for this workspace
                    try:
                        existing_company = Company.query.filter_by(workspace_id=workspace.id).first()
                        if not existing_company:
                            # Create a company for this workspace
                            new_company = Company(
                                name=workspace.name,
                                registration_number="",
                                address="",
                                industry=workspace.industry_type or '',
                                phone=workspace.company_phone or '',
                                created_by=user.id,
                                workspace_id=workspace.id
                            )
                            db.session.add(new_company)
                            db.session.commit()
                            logging.info(f"Created company for existing workspace: {workspace.name}")
                    except Exception as company_error:
                        logging.warning(f"Failed to create company for workspace: {company_error}")

        except Exception as db_error:
            logging.error(f"Database error in set_session: {db_error}")
            import traceback
            logging.error(f"Database error traceback: {traceback.format_exc()}")
            db.session.rollback()
            # Continue with session creation even if database operations fail
        
        logging.info(f"Session set successfully: {session['user']}")
        logging.info(f"Session keys: {list(session.keys())}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logging.error(f"Error setting session: {str(e)}")
        logging.error(f"Exception type: {type(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({"error": "Could not set session"}), 500

@app.route('/api/debug/activities', methods=['GET'])
def debug_activities():
    """Debug endpoint to check activity logging"""
    try:
        workspace_id = request.args.get('workspace_id')
        if not workspace_id:
            return jsonify({"error": "workspace_id required"}), 400
        
        # Check if ActivityLog table exists
        try:
            total_activities = ActivityLog.query.count()
        except Exception as table_error:
            return jsonify({
                "error": "ActivityLog table does not exist",
                "details": str(table_error),
                "workspace_id": workspace_id
            }), 500
        
        # Get activities for this workspace
        activities = ActivityLog.query.filter_by(workspace_id=workspace_id).order_by(ActivityLog.created_at.desc()).limit(10).all()
        
        activity_data = []
        for activity in activities:
            activity_data.append({
                'id': activity.id,
                'action_type': activity.action_type,
                'details': activity.details,
                'created_at': activity.created_at.isoformat() if activity.created_at else None,
                'workspace_id': activity.workspace_id
            })
        
        return jsonify({
            'workspace_id': workspace_id,
            'activity_count': len(activities),
            'activities': activity_data,
            'total_activities_in_db': total_activities
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/refresh-activities', methods=['POST'])
def refresh_activities():
    """Refresh activities by creating a test activity"""
    try:
        # Check if user is authenticated
        if 'user' not in session or 'user_email' not in session['user']:
            return jsonify({'error': 'Not authenticated'}), 401

        # Check if user has current workspace
        if 'current_workspace' not in session:
            return jsonify({'error': 'No workspace selected'}), 400

        workspace_id = session['current_workspace']['id']
        user_email = session['user']['user_email']

        # Create a test activity
        log_activity(
            action_type="system",
            resource_type="dashboard",
            description="Activity log refreshed",
            workspace_id=workspace_id,
            user_email=user_email
        )

        return jsonify({'success': True, 'message': 'Activities refreshed'})
        
    except Exception as e:
        logging.error(f"Error refreshing activities: {e}")
        return jsonify({'error': 'Failed to refresh activities'}), 500

@app.route('/api/workspace/payments', methods=['GET'])
def get_workspace_payments():
    """API endpoint to get workspace payment information (admin only)"""
    try:
        if 'current_workspace' not in session:
            return jsonify({"error": "No active workspace"}), 400
        
        workspace_id = session['current_workspace']['id']
        user_email = session['user']['user_email']
        
        user = User.query.filter_by(email=user_email).first()
        
        # Add debugging
        logging.info(f"Payments route - User: {user_email}, User ID: {user.id if user else 'None'}")
        logging.info(f"Payments route - Workspace ID: {workspace_id}")
        
        if not user:
            logging.error(f"User not found: {user_email}")
            return jsonify({"error": "User not found"}), 404
        
        # Check user's role in workspace
        user_workspace = UserWorkspace.query.filter_by(
            user_id=user.id, 
            workspace_id=workspace_id
        ).first()
        
        logging.info(f"UserWorkspace record: {user_workspace.role if user_workspace else 'None'}")
        
        if not user_workspace:
            logging.error(f"No UserWorkspace record found for user {user.id} in workspace {workspace_id}")
            return jsonify({"error": "User not found in workspace"}), 404
        
        if user_workspace.role != 'Admin':
            logging.error(f"User {user_email} has role {user_workspace.role}, but Admin required")
            return jsonify({"error": "Admin access required"}), 403
        
        workspace = Workspace.query.get(workspace_id)
        if not workspace:
            return jsonify({"error": "Workspace not found"}), 404
        
        # Calculate trial status
        now = datetime.utcnow()
        trial_days_left = (workspace.trial_end_date - now).days
        is_trial_active = trial_days_left > 0
        
        return jsonify({
            "workspace": {
                "name": workspace.name,
                "code": workspace.workspace_code,
                "subscription_status": workspace.subscription_status,
                "trial_start_date": workspace.created_at.isoformat(),
                "trial_end_date": workspace.trial_end_date.isoformat() if workspace.trial_end_date else None,
                "trial_days_left": max(0, trial_days_left),
                "is_trial_active": is_trial_active
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting workspace payments: {str(e)}")
        return jsonify({"error": "Failed to get payment information"}), 500

@app.route('/test_session_route')
def test_session_route():
    """Test endpoint to check session functionality from routes.py"""
    try:
        return jsonify({
            "session_exists": 'user' in session,
            "session_user": session.get('user'),
            "current_workspace": session.get('current_workspace'),
            "all_session_keys": list(session.keys()),
            "request_endpoint": request.endpoint,
            "request_method": request.method
        })
    except Exception as e:
        logging.error(f"Error in test_session_route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/url')
def url_route():
    """Route to handle URL requests from reports page"""
    return jsonify({'url': request.host_url.rstrip('/')})

@app.route('/runtime-app-settings-url')
def get_runtime_app_settings_url():
    try:
        # Get the base URL from environment or configuration
        base_url = os.environ.get('APP_BASE_URL', 'http://localhost:8080')
        return jsonify({"url": base_url})
    except Exception as e:
        logging.error(f"Error retrieving runtime app settings URL: {str(e)}")
        return jsonify({"error": "Could not retrieve runtime app settings URL"}), 500

@app.route('/signin')
def signin_route():
    return render_template('signin.html')

@app.route('/finishSignin', methods=['GET'])
def finish_signin_route():
    email = request.args.get('email')
    if not email:
        return redirect(url_for('signin_route'))
    return render_template('finishSignin.html')

@app.route('/payments')
def payments_route():
    """Route for payments page (admin only)"""
    return render_template('payments.html')

@app.route("/api/company/payout-rate", methods=['POST'])
def update_payout_rate():
    try:
        data = request.get_json()
        new_rate = float(data.get('rate'))
        new_currency = data.get('currency')
        new_symbol = data.get('symbol')
        
        if new_rate <= 0:
            return jsonify({'error': 'Payout rate must be greater than 0'}), 400
            
        if not new_currency or not new_symbol:
            return jsonify({'error': 'Currency and symbol are required'}), 400
            
        # Get current company from workspace
        company = get_current_company()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
            
        company.daily_payout_rate = new_rate
        company.currency = new_currency
        company.currency_symbol = new_symbol
        db.session.commit()
        
        # Log payout rate update
        log_activity(
            action_type='update',
            resource_type='company',
            description=LogMessages.COMPANY_PAYOUT_UPDATED.format(currency=new_symbol, amount=new_rate),
            resource_id=company.id,
            details={
                'old_rate': company.daily_payout_rate,
                'new_rate': new_rate,
                'old_currency': company.currency,
                'new_currency': new_currency,
                'old_symbol': company.currency_symbol,
                'new_symbol': new_symbol
            }
        )
        
        return jsonify({
            'message': 'Payout rate updated successfully',
            'new_rate': new_rate,
            'currency': new_currency,
            'symbol': new_symbol
        }), 200
        
    except ValueError:
        return jsonify({'error': 'Invalid payout rate format'}), 400
    except Exception as e:
        logging.error(f"Error updating payout rate: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update payout rate'}), 500

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route("/api/activity-logs", methods=['GET'])
def get_activity_logs():
    """Get recent activity logs"""
    try:
        # Check if user is authenticated
        if 'user' not in session or 'user_email' not in session['user']:
            logging.warning("User not authenticated for activity logs")
            return jsonify({'error': 'Not authenticated'}), 401

        # Check if user has current workspace
        if 'current_workspace' not in session:
            logging.warning("No current workspace for activity logs")
            return jsonify({'error': 'No workspace selected'}), 400

        workspace_id = session['current_workspace']['id']

        # Get query parameters
        limit = request.args.get('limit', 20, type=int)
        limit = min(limit, 100)  # Cap at 100 records
        page = request.args.get('page', 1, type=int)
        action_type = request.args.get('action_type', None)

        # Calculate offset
        offset = (page - 1) * limit

        # Get activities using the activity logger function
        from activity_logger import get_recent_activities
        activities = get_recent_activities(workspace_id, limit=limit)
        
        # Filter by action_type if provided
        if action_type:
            activities = [a for a in activities if a.get('action_type') == action_type]
        
        # Apply pagination manually
        total = len(activities)
        paginated_activities = activities[offset:offset + limit]
        has_more = (offset + limit) < total
        
        logging.info(f"Returning {len(paginated_activities)} activity logs for workspace {workspace_id}")
        
        return jsonify({
            'activities': paginated_activities,
            'total': total,
            'has_more': has_more,
            'page': page,
            'limit': limit
        })
        
    except Exception as e:
        logging.error(f"Error fetching activity logs: {e}")
        import traceback
        logging.error(f"Activity logs traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to fetch activity logs'}), 500
        
        # Apply pagination and ordering
        activities = query.order_by(
            ActivityLog.created_at.desc()
        ).offset((page - 1) * limit).limit(limit).all()
        
        # Convert to dict format
        activity_list = []
        for activity in activities:
            activity_dict = activity.to_dict()
            # Parse created_at for better formatting
            if activity.created_at:
                activity_dict['created_at_formatted'] = activity.created_at.strftime('%Y-%m-%d %H:%M:%S')
                activity_dict['time_ago'] = get_time_ago(activity.created_at)
            activity_list.append(activity_dict)
        
        logging.info(f"Returning {len(activity_list)} activities out of {total} total")
        
        return jsonify({
            'activities': activity_list,
            'total': total,
            'page': page,
            'limit': limit,
            'has_more': total > page * limit
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching activity logs: {str(e)}")
        return jsonify({'error': 'Failed to fetch activity logs'}), 500

def get_time_ago(date_time):
    """Get human-readable time difference"""
    from datetime import datetime, timezone
    
    now = datetime.utcnow()
    diff = now - date_time
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"
logger = logging.getLogger(__name__)

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"500 error: {str(error)}\n{traceback.format_exc()}")
    return render_template('500.html'), 500

@app.route("/")
def landing_route():
    return render_template("landing.html")

@app.route("/terms-of-use")
def terms_of_use_route():
    return render_template("terms_of_use.html")

@app.route("/privacy-policy")
def privacy_policy_route():
    return render_template("privacy_policy.html")

@app.route("/legal-compliance")
def legal_compliance_route():
    return render_template("legal_compliance.html")

@app.route("/logout", methods=['GET'])
def logout_route():
    session.clear()
    return redirect(url_for('landing_route'))

@app.route("/signout")
def signout():
    session.clear()
    return redirect(url_for('landing_route'))

@app.route("/api/worker", methods=['POST'])
def create_worker():
    try:
        data = request.get_json()
        
        # Get current company from workspace
        company = get_current_company()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Handle date_of_birth
        date_of_birth = None
        if data.get('date_of_birth'):
            try:
                date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format for date of birth. Use YYYY-MM-DD'}), 400
        
        # Create new worker
        new_worker = Worker(
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            date_of_birth=date_of_birth,
            company_id=company.id
        )
        db.session.add(new_worker)
        db.session.flush()  # Ensure new_worker.id is available
        # Handle custom fields
        import_fields = ImportField.query.filter_by(company_id=company.id).all()
        for field in import_fields:
            if field.name in data:
                custom_value = WorkerCustomFieldValue(
                    worker_id=new_worker.id,
                    custom_field_id=field.id,
                    value=data[field.name]
                )
                db.session.add(custom_value)
        
        db.session.commit()
        
        # Log worker creation
        worker_name = f"{new_worker.first_name} {new_worker.last_name}".strip()
        log_activity(
            action_type='create',
            resource_type='worker',
            description=LogMessages.WORKER_CREATED.format(name=worker_name),
            resource_id=new_worker.id,
            details={
                'worker_name': worker_name,
                'company_id': company.id,
                'custom_fields': {field.name: data.get(field.name) for field in import_fields if field.name in data}
            }
        )
        
        return jsonify({'message': 'Worker added successfully'}), 201
        
    except Exception as e:
        logging.error(f"Error creating worker: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to add worker'}), 500

@app.route("/api/task", methods=['POST'])
def create_task():
    try:
        data = request.get_json()
        logging.info(f"Received task creation data: {data}")
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Task name is required'}), 400
        if not data.get('start_date'):
            return jsonify({'error': 'Start date is required'}), 400
        
        # Get current company from workspace
        company = get_current_company()
        
        if not company:
            logging.error(f"Company not found for current workspace")
            return jsonify({'error': 'Company not found'}), 404
        try:
            # Parse start date
            start_date = datetime.fromisoformat(data['start_date'])
        except ValueError as e:
            logging.error(f"Invalid date format: {data['start_date']}")
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        # Date validation: start date cannot be in the past
        today = datetime.now().date()
        if start_date.date() < today:
            return jsonify({'error': 'Start date cannot be in the past.'}), 400
        # Set status based on date
        status = data.get('status', 'Pending')
        if start_date.date() == today:
            status = 'In Progress'
        elif start_date.date() > today:
            status = 'Pending'
        # Create new task
        new_task = Task(
            name=data['name'],
            description=data.get('description', ''),
            start_date=start_date,
            company_id=company.id,
            status=status,
            payment_type=data.get('payment_type', 'per_day'),
            per_part_payout=data.get('per_part_payout'),
            per_part_currency=data.get('per_part_currency')
        )
        db.session.add(new_task)
        db.session.commit()
        
        # Log task creation
        try:
            log_activity(
                action_type='create',
                resource_type='task',
                description=LogMessages.TASK_CREATED.format(name=new_task.name),
                resource_id=new_task.id,
                details={
                    'task_name': new_task.name,
                    'description': new_task.description,
                    'start_date': new_task.start_date.isoformat(),
                    'payment_type': new_task.payment_type,
                    'status': new_task.status,
                    'company_id': company.id
                }
            )
        except Exception as log_error:
            logging.warning(f"Failed to log task creation activity: {log_error}")
        
        logging.info(f"Successfully created task: {new_task.id}")
        
        return jsonify({
            'message': 'Task created successfully',
            'task_id': new_task.id
        }), 201
    except Exception as e:
        logging.error(f"Error creating task: {str(e)}\n{traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'error': f'Failed to create task: {str(e)}'}), 500

@app.route("/api/company", methods=['POST'])
def create_company():
    try:
        data = request.get_json()
        
        # Get current user
        user_email = session['user']['user_email']
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create new company
        new_company = Company(
            name=data['name'],
            registration_number=data['registration_number'],
            address=data['address'],
            industry=data['industry'],
            phone=data['phone'],
            created_by=user.id
        )
        
        db.session.add(new_company)
        db.session.commit()
        
        return jsonify({'message': 'Company created successfully'}), 201
        
    except Exception as e:
        logging.error(f"Error creating company: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create company'}), 500

@app.route("/api/company/contact", methods=['POST'])
def update_company_contact():
    try:
        # Check if user is logged in
        if 'user' not in session or 'user_email' not in session['user']:
            return jsonify({'error': 'Not authenticated'}), 401

        data = request.get_json()
        
        if not data or 'email' not in data or 'phone' not in data:
            return jsonify({'error': 'Email and phone are required'}), 400

        # Get current workspace from the session
        if 'current_workspace' not in session:
            return jsonify({'error': 'No workspace found in session'}), 404
            
        workspace_id = session['current_workspace']['id']
        workspace = Workspace.query.filter_by(id=workspace_id).first()
        
        if not workspace:
            return jsonify({'error': 'No workspace found for current session'}), 404

        # Update the workspace's email and phone
        workspace.company_email = data['email']
        workspace.company_phone = data['phone']
        
        db.session.commit()
        
        # Update the session data if it exists
        if 'current_workspace' in session and isinstance(session['current_workspace'], dict):
            session['current_workspace']['company_email'] = data['email']
            session['current_workspace']['company_phone'] = data['phone']
            session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Company contact information updated successfully'
        }), 200
        
    except Exception as e:
        logging.error(f"Error updating company contact: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update company contact information'}), 500

@app.route("/workers", methods=['GET'])
def workers_route():
    try:
        if 'user' not in session or 'user_email' not in session['user']:
            logger.error("No user in session")
            return redirect(url_for('landing_route'))
            
        user_email = session['user']['user_email']
        logger.info(f"Fetching workers for user: {user_email}")
        
        user = User.query.filter_by(email=user_email).first()
        if not user:
            logger.error(f"User not found: {user_email}")
            return redirect(url_for('landing_route'))
        
        # Get company from current workspace
        if 'current_workspace' not in session:
            logger.error(f"No active workspace for user: {user_email}")
            return redirect(url_for('workspace_selection_route'))
            
        workspace_id = session['current_workspace']['id']
        company = Company.query.filter_by(workspace_id=workspace_id).first()
        if not company:
            logger.info(f"No company found for workspace: {workspace_id}")
            return render_template('workers.html', workers=[], all_fields=[])

        # Get custom fields for this company
        custom_fields = ImportField.query.filter_by(company_id=company.id).all()
        default_fields = [
            {'name': 'First Name', 'type': 'text', 'id': 'first_name'},
            {'name': 'Last Name', 'type': 'text', 'id': 'last_name'},
            {'name': 'Date of Birth', 'type': 'date', 'id': 'date_of_birth'}
        ]
        all_fields = default_fields + [{'name': field.name, 'type': field.field_type or 'text', 'id': field.id} for field in custom_fields]
        
        # Get workers for this company with their custom field values
        workers = Worker.query.filter_by(company_id=company.id).all()
        logger.info(f"Found {len(workers)} workers for company ID: {company.id}")
        
        # Debug logging for workers
        for worker in workers:
            logger.info(f"Worker ID: {worker.id}, First Name: {worker.first_name}, Last Name: {worker.last_name}")
            
            # Log custom field values
            custom_values = WorkerCustomFieldValue.query.filter_by(worker_id=worker.id).all()
            for value in custom_values:
                logger.info(f"Custom Field ID: {value.custom_field_id}, Value: {value.value}")
        
        return render_template('workers.html', workers=workers, all_fields=all_fields)
    except Exception as e:
        logger.error(f"Error in workers_route: {str(e)}")
        return render_template('500.html'), 500
        logger.error(f"Error in workers_route: {str(e)}\n{traceback.format_exc()}")
        return render_template('500.html'), 500

@app.route("/api/import-field", methods=['GET', 'POST'])
def import_field():
    try:
        # Get current company from workspace
        company = get_current_company()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
            
        if request.method == 'GET':
            fields = ImportField.query.filter_by(company_id=company.id).all()
            return jsonify([{
                'id': field.id,
                'name': field.name,
                'field_type': field.field_type
            } for field in fields])
            
        data = request.get_json()
        
        # Validate required fields
        if not data or 'name' not in data:
            return jsonify({'error': 'Field name is required'}), 400
        
        # Create new import field
        new_field = ImportField(
            company_id=company.id,
            name=data['name'],
            field_type=data.get('type', 'text')  # Default to 'text' if type is not provided
        )
        
        db.session.add(new_field)
        db.session.commit()
        
        return jsonify({
            'id': new_field.id,
            'name': new_field.name,
            'type': new_field.field_type
        }), 201
        
    except Exception as e:
        logging.error(f"Error handling import field: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to handle import field request'}), 500

@app.route("/api/import-field/<int:field_id>", methods=['DELETE'])
def delete_import_field(field_id):
    try:
        # Get current company from workspace
        company = get_current_company()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
            
        # Find and delete field
        field = ImportField.query.filter_by(id=field_id, company_id=company.id).first()
        
        if not field:
            return jsonify({'error': 'Field not found'}), 404
            
        db.session.delete(field)
        db.session.commit()
        
        return jsonify({'message': 'Field deleted successfully'}), 200
        
    except Exception as e:
        logging.error(f"Error deleting import field: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete import field'}), 500

from abilities import llm

@app.route("/api/worker/import", methods=['POST'])
def import_workers():
    try:
        # Validate upload
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Invalid file format. Please upload an Excel file'}), 400

        # Save file using existing helpers – returns a storage identifier we can reuse later
        file_id = upload_file_to_storage(file)
        file_path = file_id  # upload_file_to_storage already returns the full path

        # Analyse the Excel contents – get column names and a small preview (first 5 rows)
        df = pd.read_excel(file_path, na_filter=False).dropna(how='all')
        columns = list(df.columns)
        preview = df.head(5).to_dict(orient='records')

        return jsonify({
            'columns': columns,
            'preview': preview,
            'file_id': file_id
        }), 200
    except Exception as e:
        logging.error(f"Error analysing Excel file: {str(e)}")
        return jsonify({'error': 'Failed to analyse Excel file'}), 500
@app.route("/tasks", methods=['GET'])
def tasks_route():
    try:
        from datetime import date
        # Get current company from workspace
        company = get_current_company()

        if not company:
            return render_template('tasks.html', tasks=[], task_statuses=['Pending', 'In Progress', 'Completed'], today_date=date.today().strftime('%Y-%m-%d'))

        tasks = Task.query.filter_by(company_id=company.id).all()
        return render_template('tasks.html', tasks=tasks, task_statuses=['Pending', 'In Progress', 'Completed'], today_date=date.today().strftime('%Y-%m-%d'))
    except Exception as e:
        logging.error(f"Error fetching tasks: {str(e)}")
        return render_template('500.html'), 500

@app.route("/task/<int:task_id>/attendance", methods=['GET'])
def task_attendance_route(task_id):
    try:
        # Get current company from workspace
        company = get_current_company()

        if not company:
            return render_template('task_attendance.html', task=None, attendance_records=[], workers=[], selected_date=None)

        # Get the specific task
        task = Task.query.filter_by(id=task_id, company_id=company.id).first()

        if not task:
            return render_template('500.html'), 500

        # Get all available workers for the company for the dropdown
        available_workers = Worker.query.filter_by(company_id=company.id).all()

        # Get selected date from query parameter, default to today
        from datetime import date
        selected_date_str = request.args.get('date')
        if selected_date_str:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        else:
            selected_date = date.today()

        # If selected date is before task start date, show error and do not show attendance UI
        if selected_date < task.start_date.date():
            return render_template('task_attendance.html', 
                task=task, 
                attendance_records=[],
                workers=[],
                available_workers=available_workers,
                selected_date=selected_date,
                attendance_date_error="Attendance cannot be recorded before the task's start date."
            )

        # Get attendance records for the selected date
        attendance_records = Attendance.query.filter(
            Attendance.company_id == company.id,
            Attendance.date == selected_date,
            Attendance.task_id == task.id
        ).all()

        # Create attendance records for assigned workers if they don't exist
        existing_worker_ids = {record.worker_id for record in attendance_records}
        for worker in task.workers:
            if worker.id not in existing_worker_ids:
                new_attendance = Attendance(
                    worker_id=worker.id,
                    company_id=company.id,
                    date=selected_date,
                    status='Absent',
                    task_id=task.id
                )
                db.session.add(new_attendance)
        db.session.commit()

        # Fetch attendance records again to ensure up-to-date list
        attendance_records = Attendance.query.filter(
            Attendance.company_id == company.id,
            Attendance.date == selected_date,
            Attendance.task_id == task.id
        ).all()

        return render_template('task_attendance.html', 
            task=task, 
            attendance_records=attendance_records,
            workers=task.workers.all(),  # Only show assigned workers
            available_workers=available_workers,  # Pass all available workers for dropdown
            selected_date=selected_date,
            attendance_date_error=None
        )
    except Exception as e:
        logging.error(f"Error fetching task attendance: {str(e)}")
        return render_template('500.html'), 500


@app.route("/home", methods=['GET'])
def home_route():
    try:
        # Check if user is authenticated
        if 'user' not in session or 'user_email' not in session['user']:
            logging.info("User not authenticated, redirecting to signin")
            return redirect(url_for('signin_route'))
        
        # Get current user and workspace
        user_email = session['user']['user_email']
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            logging.error(f"User not found in database: {user_email}")
            return redirect(url_for('signin_route'))
        
        if 'current_workspace' not in session:
            logging.info("No current workspace, redirecting to workspace selection")
            return redirect(url_for('workspace_selection_route'))
        
        workspace_id = session['current_workspace']['id']
        workspace = Workspace.query.get(workspace_id)
        
        if not workspace:
            logging.error(f"Workspace not found: {workspace_id}")
            session.pop('current_workspace', None)
            return redirect(url_for('workspace_selection_route'))
        
        # Check if user has access to this workspace
        user_workspace = UserWorkspace.query.filter_by(
            user_id=user.id,
            workspace_id=workspace_id
        ).first()
        
        if not user_workspace:
            logging.error(f"User {user_email} does not have access to workspace {workspace_id}")
            session.pop('current_workspace', None)
            return redirect(url_for('workspace_selection_route'))
        
        company = Company.query.filter_by(workspace_id=workspace_id).first()

        if not company:
            return render_template('home.html', company=None, total_workers=0, total_tasks=0, team_members=[])

        # Calculate total workers for the company
        total_workers = Worker.query.filter_by(company_id=company.id).count()

        # Calculate total tasks for the company
        total_tasks = Task.query.filter_by(company_id=company.id).count()

        # Get team members for this workspace
        user_workspaces = UserWorkspace.query.filter_by(workspace_id=workspace_id).all()
        team_members = []
        for uw in user_workspaces:
            user_obj = User.query.get(uw.user_id)
            if user_obj:
                team_members.append({
                    'id': user_obj.id,
                    'email': user_obj.email,
                    'role': uw.role
                })

        # Get recent activities for this workspace (with error handling)
        recent_activities = []
        activity_stats = {}
        try:
            recent_activities = get_recent_activities(workspace_id, limit=20)
            activity_stats = get_activity_stats(workspace_id, days=7)
            
            # Debug logging for activities
            logging.info(f"Dashboard - Workspace ID: {workspace_id}")
            logging.info(f"Dashboard - Recent activities count: {len(recent_activities)}")
            if recent_activities:
                logging.info(f"Dashboard - Sample activity: {recent_activities[0]}")
            else:
                # Check if there are any activities at all in the database
                total_activities = ActivityLog.query.count()
                workspace_activities = ActivityLog.query.filter(ActivityLog.workspace_id == workspace_id).count()
                logging.info(f"Dashboard - Total activities in DB: {total_activities}")
                logging.info(f"Dashboard - Activities for workspace {workspace_id}: {workspace_activities}")
                
                # Create a welcome activity if none exist for this workspace
                if workspace_activities == 0:
                    try:
                        log_activity(
                            action_type="system",
                            resource_type="dashboard",
                            description="Welcome to your dashboard! Start by creating tasks or adding workers.",
                            workspace_id=workspace_id,
                            user_email=user_email
                        )
                        logging.info("Created welcome activity for new workspace")
                    except Exception as welcome_error:
                        logging.error(f"Failed to create welcome activity: {welcome_error}")
                        
        except Exception as activity_error:
            logging.error(f"Error fetching activities: {str(activity_error)}")
            # Continue without activities if there's an error
            recent_activities = []
            activity_stats = {}

        return render_template('home.html', 
                             company=company, 
                             total_workers=total_workers, 
                             total_tasks=total_tasks, 
                             team_members=team_members,
                             recent_activities=recent_activities,
                             activity_stats=activity_stats)
    except Exception as e:
        logging.error(f"Error fetching home data: {str(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        return render_template('500.html'), 500

@app.route("/api/team-member", methods=['POST'])
def add_team_member():
    try:
        # Check if current user is a Supervisor
        if session.get('current_workspace', {}).get('role') == 'Supervisor':
            return jsonify({'error': 'Supervisors cannot add team members'}), 403
        
        data = request.get_json()
        email = data.get('email')
        role = data.get('role')

        if not email or not role:
            return jsonify({'error': 'Email and role are required'}), 400

        # Get current workspace
        workspace_id = session.get('current_workspace', {}).get('id')
        if not workspace_id:
            return jsonify({'error': 'No active workspace'}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            # Check if user is already a member of this workspace
            existing_user_workspace = UserWorkspace.query.filter_by(
                user_id=existing_user.id,
                workspace_id=workspace_id
            ).first()
            
            if existing_user_workspace:
                return jsonify({'error': 'User is already a member of this workspace'}), 400
        else:
            # Create new user if they don't exist
            existing_user = User(email=email)
            db.session.add(existing_user)
            db.session.commit()

        # Add user to workspace
        user_workspace = UserWorkspace(
            user_id=existing_user.id,
            workspace_id=workspace_id,
            role=role
        )
        db.session.add(user_workspace)
        db.session.commit()

        # Log team member addition
        log_activity(
            action_type='create',
            resource_type='team_member',
            description=LogMessages.TEAM_MEMBER_ADDED.format(email=email, role=role),
            resource_id=existing_user.id,
            details={
                'user_email': email,
                'user_id': existing_user.id,
                'role': role,
                'workspace_id': workspace_id
            }
        )

        return jsonify({
            'message': 'Team member added successfully',
            'user': {
                'id': existing_user.id,
                'email': existing_user.email,
                'role': role
            }
        }), 201

    except Exception as e:
        logging.error(f"Error adding team member: {str(e)}\n{traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'error': f'Failed to add team member: {str(e)}'}), 500

@app.route("/api/team-member/<int:user_id>/role", methods=['PUT'])
def update_team_member_role(user_id):
    try:
        # Check if current user is a Supervisor
        if session.get('current_workspace', {}).get('role') == 'Supervisor':
            return jsonify({'error': 'Supervisors cannot update team member roles'}), 403
        
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({'error': 'Role is required'}), 400
        
        # Get current workspace
        workspace_id = session.get('current_workspace', {}).get('id')
        if not workspace_id:
            return jsonify({'error': 'No active workspace'}), 400
        
        # Find the user's workspace role
        user_workspace = UserWorkspace.query.filter_by(
            user_id=user_id,
            workspace_id=workspace_id
        ).first()
        
        if not user_workspace:
            return jsonify({'error': 'User not found in this workspace'}), 404
        
        user_workspace.role = new_role
        db.session.commit()
        
        return jsonify({
            'message': 'Role updated successfully',
            'user': {
                'id': user_id,
                'email': user_workspace.user.email,
                'role': new_role
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error updating team member role: {str(e)}\n{traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'error': f'Failed to update role: {str(e)}'}), 500

@app.route("/api/team-member/<int:user_id>", methods=['DELETE'])
def delete_team_member(user_id):
    try:
        # Check if current user is a Supervisor
        if session.get('current_workspace', {}).get('role') == 'Supervisor':
            return jsonify({'error': 'Supervisors cannot delete team members'}), 403
        
        # Get current workspace
        workspace_id = session.get('current_workspace', {}).get('id')
        if not workspace_id:
            return jsonify({'error': 'No active workspace'}), 400
        
        # Get current user
        user_email = session['user']['user_email']
        current_user = User.query.filter_by(email=user_email).first()
        
        # Prevent deleting the current user
        if current_user.id == user_id:
            return jsonify({'error': 'Cannot remove yourself from the workspace'}), 400
        
        # Find the user's workspace membership
        user_workspace = UserWorkspace.query.filter_by(
            user_id=user_id,
            workspace_id=workspace_id
        ).first()
        
        if not user_workspace:
            return jsonify({'error': 'User not found in this workspace'}), 404
            
        # Remove user from workspace (but don't delete the user account)
        db.session.delete(user_workspace)
        db.session.commit()
        
        return jsonify({'message': 'Team member removed from workspace successfully'}), 200
        
    except Exception as e:
        logging.error(f"Error deleting team member: {str(e)}\n{traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'error': f'Failed to delete team member: {str(e)}'}), 500

@app.route("/attendance", methods=['GET'])
def attendance_route():
    try:
        from datetime import date, datetime
        # Get current user's company
        user_email = session['user']['user_email']
        company = get_current_company()

        if not company:
            return render_template('attendance.html', attendance_records=[])

        # Get date range from query parameters or use default (last 30 days)
        end_date = datetime.strptime(request.args.get('end_date', date.today().isoformat()), '%Y-%m-%d').date()
        start_date = datetime.strptime(request.args.get('start_date', (end_date - timedelta(days=30)).isoformat()), '%Y-%m-%d').date()

        attendance_records = Attendance.query.filter(
            Attendance.company_id == company.id,
            Attendance.date.between(start_date, end_date)
        ).all()

        return render_template('attendance.html', 
            attendance_records=attendance_records, 
            start_date=start_date, 
            end_date=end_date
        )
    except Exception as e:
        logging.error(f"Error fetching attendance: {str(e)}")
        return render_template('500.html'), 500

@app.route("/reports", methods=['GET'])
def reports_route():
    try:
        from datetime import date, timedelta, datetime
        # Get current company from workspace
        company = get_current_company()

        if not company:
            return render_template('reports.html', report_data={}, custom_fields=[], preview_records=[], import_fields=[], per_day_records=[], per_part_records=[])

        # Get date range from query parameters or use default (last 30 days)
        end_date_param = request.args.get('end_date')
        start_date_param = request.args.get('start_date')
        
        if end_date_param and start_date_param:
            # Use provided dates
            end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
            start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
        else:
            # Use default dates (last 30 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

        # Get custom report fields
        custom_fields = ReportField.query.filter_by(company_id=company.id).all()
        # Get import fields (custom worker fields)
        import_fields = ImportField.query.filter_by(company_id=company.id).all()
        # Get all tasks for the company
        tasks = Task.query.filter_by(company_id=company.id).all()
        # Get all workers for the company
        workers = Worker.query.filter_by(company_id=company.id).all()

        # Helper for formula evaluation
        def evaluate_formula(formula, context, custom_fields_dict=None, visited=None):
            if visited is None:
                visited = set()
            try:
                import re
                eval_formula = formula
                field_regex = r'[a-zA-Z_][a-zA-Z0-9_]*'
                field_matches = re.findall(field_regex, eval_formula)
                for field_name in field_matches:
                    if field_name in visited:
                        continue
                    if field_name in context:
                        value = context[field_name]
                    elif custom_fields_dict and field_name in custom_fields_dict:
                        visited.add(field_name)
                        custom_field_formula = custom_fields_dict[field_name]
                        value = evaluate_formula(custom_field_formula, context, custom_fields_dict, visited)
                        visited.remove(field_name)
                    else:
                        value = 0
                    eval_formula = re.sub(r'\b' + re.escape(field_name) + r'\b', str(value), eval_formula)
                result = eval(eval_formula)
                return round(result, 2)
            except Exception as e:
                logging.error(f"Error evaluating formula {formula}: {str(e)}")
                return 0.00

        # Prepare per_day and per_part records
        per_day_records = []
        per_part_records = []

        for worker in workers:
            # For Per Day: attendance and payout
            attendance_days = 0
            # For Per Part: units completed
            total_units_completed = 0
            # Find all attendance records for this worker in the date range
            attendance_records = Attendance.query.filter(
                Attendance.worker_id == worker.id,
                Attendance.company_id == company.id,
                Attendance.date.between(start_date, end_date)
            ).all()
            # Group by task payment type
            per_day_attendance = {}
            per_part_units = {}
            for att in attendance_records:
                if att.task and getattr(att.task, 'payment_type', None) == 'per_day':
                    if att.status == 'Present':
                        per_day_attendance.setdefault(att.task_id, 0)
                        per_day_attendance[att.task_id] += 1
                elif att.task and getattr(att.task, 'payment_type', None) == 'per_part':
                    if att.units_completed:
                        per_part_units.setdefault(att.task_id, 0)
                        per_part_units[att.task_id] += att.units_completed
            # For each per_day task, add a record
            for task_id, days in per_day_attendance.items():
                task = Task.query.get(task_id) if task_id else None
                # Compute age
                try:
                    from datetime import date
                    if worker.date_of_birth:
                        today = date.today()
                        age = today.year - worker.date_of_birth.year - ((today.month, today.day) < (worker.date_of_birth.month, worker.date_of_birth.day))
                    else:
                        age = 0
                except Exception:
                    age = 0
                record = {
                    'first_name': getattr(worker, 'first_name', ''),
                    'last_name': getattr(worker, 'last_name', ''),
                    'task_name': getattr(task, 'name', '') if task else '',
                    'attendance_days': days,
                    'daily_rate': getattr(company, 'daily_payout_rate', None),
                    'age': age,
                }
                # Add import field values
                for field in import_fields:
                    custom_value = WorkerCustomFieldValue.query.filter_by(
                        worker_id=worker.id,
                        custom_field_id=field.id
                    ).first()
                    record[field.name] = custom_value.value if custom_value else 'N/A'
                # Add custom report fields
                custom_fields_dict = {field.name: field.formula for field in custom_fields if field.field_type == 'numeric'}
                for field in custom_fields:
                    if field.field_type == 'numeric':
                        try:
                            context = {
                                'attendance_days': days,
                                'daily_rate': getattr(company, 'daily_payout_rate', None),
                                **record
                            }
                            result = evaluate_formula(field.formula, context, custom_fields_dict)
                            if field.max_limit is not None:
                                result = min(result, field.max_limit)
                            record[field.name] = result
                        except Exception as e:
                            logging.error(f"Error calculating field {field.name}: {str(e)}")
                            record[field.name] = 0.00
                per_day_records.append(record)
            # For each per_part task, add a record
            for task_id, units in per_part_units.items():
                task = Task.query.get(task_id) if task_id else None
                # Compute age
                try:
                    from datetime import date
                    if worker.date_of_birth:
                        today = date.today()
                        age = today.year - worker.date_of_birth.year - ((today.month, today.day) < (worker.date_of_birth.month, worker.date_of_birth.day))
                    else:
                        age = 0
                except Exception:
                    age = 0
                record = {
                    'first_name': getattr(worker, 'first_name', ''),
                    'last_name': getattr(worker, 'last_name', ''),
                    'task_name': getattr(task, 'name', '') if task else '',
                    'units_completed': units,
                    'per_part_rate': getattr(task, 'per_part_payout', None) if task else None,
                    'per_part_currency': getattr(task, 'per_part_currency', None) if task else None,
                    'age': age,
                }
                # Add import field values
                for field in import_fields:
                    custom_value = WorkerCustomFieldValue.query.filter_by(
                        worker_id=worker.id,
                        custom_field_id=field.id
                    ).first()
                    record[field.name] = custom_value.value if custom_value else 'N/A'
                # Add custom report fields for per_part
                per_part_custom_fields = [f for f in custom_fields if f.payout_type in ('per_part', 'both')]
                custom_fields_dict = {field.name: field.formula for field in per_part_custom_fields if field.field_type == 'numeric'}
                for field in per_part_custom_fields:
                    if field.field_type == 'numeric':
                        try:
                            context = {
                                'units_completed': units,
                                'per_part_rate': record['per_part_rate'],
                                **record
                            }
                            result = evaluate_formula(field.formula, context, custom_fields_dict)
                            if field.max_limit is not None:
                                result = min(result, field.max_limit)
                            record[field.name] = result
                        except Exception as e:
                            logging.error(f"Error calculating field {field.name}: {str(e)}")
                            record[field.name] = 0.00
                per_part_records.append(record)

        return render_template('reports.html', 
            report_data={}, 
            custom_fields=custom_fields,
            import_fields=import_fields,
            per_day_records=per_day_records,
            per_part_records=per_part_records
        )
    except Exception as e:
        logging.error(f"Error generating reports: {str(e)}")
        return render_template('500.html'), 500
@app.route("/api/worker/analyze-columns", methods=['POST'])
def analyze_columns():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Invalid file format. Please upload an Excel file'}), 400
        file_id = upload_file_to_storage(file)
        file_path = file_id  # upload_file_to_storage already returns the full path
        df = pd.read_excel(file_path, na_filter=False)
        df = df.dropna(how='all')
        original_columns = list(df.columns)
        logging.info(f"Excel columns found: {original_columns}")
        
        # Return column names and file_id with consistent keys
        return jsonify({
            'columns': original_columns,  # Changed from 'original_columns'
            'file_id': file_id,
            'original_columns': original_columns  # Keep original for backwards compatibility
        }), 200
    except Exception as e:
        logging.error(f"Error analyzing columns: {str(e)}")
        return jsonify({'error': f'Failed to analyze Excel file: {str(e)}'}), 500
@app.route("/api/worker/import-mapped", methods=['POST'])
def import_mapped_workers():
    try:
        mapping_str = request.form.get('mapping')
        if not mapping_str:
            return jsonify({'error': 'Mapping not provided'}), 400
        import json
        mapping = json.loads(mapping_str)
        file_id = request.form.get('file_id')
        if not file_id:
            return jsonify({'error': 'File ID not provided'}), 400
        file_path = file_id  # The file_id we stored is the actual path on disk
        df = pd.read_excel(file_path, na_filter=False)
        df = df.dropna(how='all')
        
        # Log the mapping for debugging
        logging.info(f"Column mapping: {mapping}")
        
        # Get current user and company
        user_email = session['user']['user_email']
        user = User.query.filter_by(email=user_email).first()
        company = get_current_company()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        total_records = len(df)
        successful_imports = 0
        duplicate_records = 0
        error_records = 0
        error_details = []
        
        for index, row in df.iterrows():
            try:
                # Create new worker with mapped data
                worker_data = {}
                custom_field_data = {}
                
                for field, excel_col in mapping.items():
                    if pd.notna(row[excel_col]):
                        # Separate worker fields from custom fields
                        if field in ['first_name', 'last_name', 'date_of_birth']:
                            value = str(row[excel_col]).strip()
                            if field == 'date_of_birth':
                                try:
                                    value = pd.to_datetime(value).date()
                                except Exception as e:
                                    logging.warning(f"Could not parse date_of_birth: {value}")
                                    value = None
                            worker_data[field] = value
                        else:
                            custom_field_data[field] = str(row[excel_col]).strip()
                
                logging.info(f"Processed data for row {index}: {worker_data}")

                # Duplicate check – skip if a worker with the same first & last name already exists for this company
                if worker_data.get('first_name') and worker_data.get('last_name'):
                    duplicate = Worker.query.filter_by(
                        first_name=worker_data.get('first_name'),
                        last_name=worker_data.get('last_name'),
                        company_id=company.id
                    ).first()
                    if duplicate:
                        duplicate_records += 1
                        continue
                
                new_worker = Worker(
                    first_name=worker_data.get('first_name', ''),
                    last_name=worker_data.get('last_name', ''),
                    date_of_birth=worker_data.get('date_of_birth', None),
                    company_id=company.id,
                    user_id=user.id
                )
                db.session.add(new_worker)
                db.session.flush()
                
                # Add custom field values
                for field_name, value in custom_field_data.items():
                    # If the mapping key is a numeric ID (as the UI sends for existing custom fields), use it directly
                    if str(field_name).isdigit():
                        import_field = ImportField.query.filter_by(
                            id=int(field_name),
                            company_id=company.id
                        ).first()
                    else:
                        import_field = ImportField.query.filter_by(
                            name=field_name,
                            company_id=company.id
                        ).first()
                    
                    if not import_field:
                        import_field = ImportField(
                            name=field_name, 
                            company_id=company.id,
                            field_type='text'  # Default type
                        )
                        db.session.add(import_field)
                        db.session.flush()
                    
                    # Create custom field value
                    custom_value = WorkerCustomFieldValue(
                        worker_id=new_worker.id,
                        custom_field_id=import_field.id,
                        value=value
                    )
                    db.session.add(custom_value)
                
                db.session.commit()
                successful_imports += 1
                logging.info(f"Successfully imported worker: {new_worker.first_name} {new_worker.last_name}")
                
            except Exception as e:
                # If something goes wrong with this row, undo its partial changes but keep previous rows intact
                db.session.rollback()  # rollback JUST the un-committed state for this iteration
                error_records += 1
                error_details.append(f"Row {index + 2}: {str(e)}")
                logging.error(f"Error processing row {index + 2}: {str(e)}")
                continue  # proceed with next row
        
        db.session.commit()
        
        # Create import log
        import_log = WorkerImportLog(
            company_id=company.id,
            filename="Mapped Import",
            total_records=total_records,
            successful_imports=successful_imports,
            duplicate_records=duplicate_records,
            error_records=error_records,
            error_details='\n'.join(error_details) if error_details else None
        )
        db.session.add(import_log)
        db.session.commit()
        
        os.remove(file_path)
        
        return jsonify({
            'message': 'Import completed',
            'total_records': total_records,
            'successful_imports': successful_imports,
            'duplicate_records': duplicate_records,
            'error_records': error_records,
            'error_details': error_details
        }), 200
    except Exception as e:
        logging.error(f"Error importing mapped workers: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to import workers'}), 500
@app.route("/api/worker/<int:worker_id>", methods=['DELETE'])
def delete_worker(worker_id):
    try:
        # Get current company from workspace
        company = get_current_company()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
            
        # Find worker and verify they belong to user's company
        worker = Worker.query.filter_by(id=worker_id, company_id=company.id).first()
        
        if not worker:
            return jsonify({'error': 'Worker not found'}), 404
            
        # Delete custom field values first
        WorkerCustomFieldValue.query.filter_by(worker_id=worker_id).delete()
        
        # Delete attendance records
        Attendance.query.filter_by(worker_id=worker_id).delete()
        
        # Delete worker
        db.session.delete(worker)
        db.session.commit()
        
        logging.info(f"Worker {worker_id} deleted from company {company.id}")
        return jsonify({'message': 'Worker deleted successfully'}), 200
        
    except Exception as e:
        logging.error(f"Error deleting worker: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete worker'}), 500

@app.route("/api/worker/<int:worker_id>", methods=['PUT'])
def update_worker(worker_id):
    try:
        data = request.get_json()
        # Get current company from workspace
        company = get_current_company()
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        worker = Worker.query.filter_by(id=worker_id, company_id=company.id).first()
        if not worker:
            return jsonify({'error': 'Worker not found'}), 404
        # Handle date_of_birth
        if 'date_of_birth' in data:
            if data['date_of_birth']:
                try:
                    worker.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid date format for date of birth. Use YYYY-MM-DD'}), 400
            else:
                worker.date_of_birth = None
        
        # Update default fields
        worker.first_name = data.get('first_name', worker.first_name)
        worker.last_name = data.get('last_name', worker.last_name)
        # Update custom fields
        import_fields = ImportField.query.filter_by(company_id=company.id).all()
        for field in import_fields:
            if field.name in data:
                custom_value = WorkerCustomFieldValue.query.filter_by(worker_id=worker.id, custom_field_id=field.id).first()
                if custom_value:
                    custom_value.value = data[field.name]
                else:
                    new_value = WorkerCustomFieldValue(worker_id=worker.id, custom_field_id=field.id, value=data[field.name])
                    db.session.add(new_value)
        db.session.commit()
        return jsonify({'message': 'Worker updated successfully'}), 200
    except Exception as e:
        logging.error(f"Error updating worker: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update worker'}), 500

@app.route("/api/task/<int:task_id>/attendance", methods=['POST'])
def update_task_attendance(task_id):
    try:
        # Get current company from workspace
        company = get_current_company()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Get the task
        task = Task.query.filter_by(id=task_id, company_id=company.id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        attendance_data = data.get('attendance_data', [])
        selected_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        
        # Validation: Prevent attendance before task start date
        if selected_date < task.start_date.date():
            return jsonify({'error': 'You cannot record attendance before the task start date.'}), 400
        
        # Update attendance records
        for record in attendance_data:
            worker_id = record.get('worker_id')
            status = record.get('status')
            units_completed = record.get('units_completed')
            
            # Create new attendance record if it doesn't exist
            attendance = Attendance.query.filter_by(
                worker_id=worker_id, 
                company_id=company.id, 
                date=selected_date,
                task_id=task.id
            ).first()
            
            if attendance:
                if status is not None:
                    attendance.status = status
                if units_completed is not None:
                    attendance.units_completed = units_completed
            else:
                new_attendance = Attendance(
                    worker_id=worker_id,
                    company_id=company.id,
                    date=selected_date,
                    status=status if status is not None else 'Absent',
                    task_id=task.id,
                    units_completed=units_completed
                )
                db.session.add(new_attendance)
        
        db.session.commit()
        
        return jsonify({'message': 'Attendance updated successfully'}), 200
        
    except Exception as e:
        logging.error(f"Error updating task attendance: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update task attendance'}), 500

@app.route("/api/task/<int:task_id>/add-worker", methods=['POST'])
def add_worker_to_task(task_id):
    try:
        # Get current company from workspace
        company = get_current_company()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Get the task
        task = Task.query.filter_by(id=task_id, company_id=company.id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        worker_id = data.get('worker_id')
        
        # Validate worker belongs to the company
        worker = Worker.query.filter_by(id=worker_id, company_id=company.id).first()
        if not worker:
            return jsonify({'error': 'Invalid worker'}), 400
        
        # Prevent duplicate assignment
        if worker in task.workers:
            return jsonify({'error': 'This worker is already assigned to this task.'}), 400
        
        # Add worker to task's workers list
        task.workers.append(worker)
        db.session.commit()
        
        # Create attendance record for the worker for the task's start date
        attendance = Attendance(
            worker_id=worker_id,
            company_id=company.id,
            date=task.start_date.date(),
            status='Absent',  # Default status when adding worker
            task_id=task.id
        )
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({
            'message': 'Worker added to task successfully',
            'worker_id': worker_id
        }), 200
        
    except Exception as e:
        logging.error(f"Error adding worker to task: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to add worker to task'}), 500

@app.route("/api/worker/bulk-delete", methods=['POST'])
def bulk_delete_workers():
    try:
        data = request.get_json()
        # Convert all worker_ids to integers and filter out invalids
        worker_ids = [int(wid) for wid in data.get('worker_ids', []) if str(wid).isdigit()]
        if not worker_ids:
            return jsonify({'error': 'No worker IDs provided'}), 400

        # Get current company from workspace
        company = get_current_company()
        if not company:
            return jsonify({'error': 'Company not found'}), 404

        # Only delete workers belonging to this company
        workers = Worker.query.filter(Worker.id.in_(worker_ids), Worker.company_id == company.id).all()
        if not workers:
            return jsonify({'error': 'No matching workers found'}), 404

        # Delete related custom field values and attendance records
        WorkerCustomFieldValue.query.filter(WorkerCustomFieldValue.worker_id.in_(worker_ids)).delete(synchronize_session=False)
        Attendance.query.filter(Attendance.worker_id.in_(worker_ids)).delete(synchronize_session=False)
        Worker.query.filter(Worker.id.in_(worker_ids), Worker.company_id == company.id).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'message': f'{len(worker_ids)} workers deleted successfully'}), 200
    except Exception as e:
        logging.error(f"Error bulk deleting workers: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to bulk delete workers'}), 500

@app.route("/api/task/<int:task_id>/update-date", methods=['POST'])
def update_task_date(task_id):
    try:
        # Get current company from workspace
        company = get_current_company()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Get the task
        task = Task.query.filter_by(id=task_id, company_id=company.id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        new_start_date = datetime.fromisoformat(data.get('start_date'))
        
        # Update task start date
        task.start_date = new_start_date
        
        # Update or create attendance records for the new date
        Attendance.query.filter_by(
            company_id=company.id, 
            date=task.start_date.date()
        ).delete()
        
        db.session.commit()
        
        return jsonify({'message': 'Task date updated successfully'}), 200
        
    except Exception as e:
        logging.error(f"Error updating task date: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update task date'}), 500

@app.route("/api/task/<int:task_id>", methods=['DELETE'])
def delete_task(task_id):
    try:
        # Get current company from workspace
        company = get_current_company()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Get the task
        task = Task.query.filter_by(id=task_id, company_id=company.id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
            
        # Delete attendance records for this task
        Attendance.query.filter_by(
            task_id=task.id
        ).delete()
        
        # Delete task
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    except Exception as e:
        logging.error(f"Error deleting task: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete task'}), 500

@app.route("/api/task/<int:task_id>/status", methods=['POST'])
def update_task_status(task_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
            
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
            
        # Update status and handle completion date
        task.status = new_status
        if new_status == 'Completed' and not task.completion_date:
            task.completion_date = datetime.utcnow()
        elif new_status != 'Completed':
            task.completion_date = None
            
        db.session.commit()
        
        return jsonify({
            'message': 'Task status updated successfully',
            'status': new_status,
            'completion_date': task.completion_date.strftime('%Y-%m-%d %H:%M:%S') if task.completion_date else None
        }), 200
        
    except Exception as e:
        logging.error(f"Error updating task status: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update task status'}), 500

from abilities import llm

@app.route("/report/download")
def download_report():
    try:
        # Get current company from workspace
        company = get_current_company()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
            
        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'Date range required'}), 400
        from datetime import datetime
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        # Get all workers for the company
        workers = Worker.query.filter_by(company_id=company.id).all()
        import_fields = ImportField.query.filter_by(company_id=company.id).all()
        custom_fields = ReportField.query.filter_by(company_id=company.id).all()

        report_type = request.args.get('report_type')
        # Filter custom fields by report type
        if report_type == 'per_day':
            relevant_custom_fields = [f for f in custom_fields if f.payout_type in ('per_day', 'both')]
        elif report_type == 'per_part':
            relevant_custom_fields = [f for f in custom_fields if f.payout_type in ('per_part', 'both')]
        else:
            relevant_custom_fields = custom_fields  # fallback: include all

        # Helper for formula evaluation
        def evaluate_formula(formula, context, custom_fields_dict=None, visited=None):
            if visited is None:
                visited = set()
            try:
                import re
                eval_formula = formula
                field_regex = r'[a-zA-Z_][a-zA-Z0-9_]*'
                field_matches = re.findall(field_regex, eval_formula)
                for field_name in field_matches:
                    if field_name in visited:
                        continue
                    if field_name in context:
                        value = context[field_name]
                    elif custom_fields_dict and field_name in custom_fields_dict:
                        visited.add(field_name)
                        custom_field_formula = custom_fields_dict[field_name]
                        value = evaluate_formula(custom_field_formula, context, custom_fields_dict, visited)
                        visited.remove(field_name)
                    else:
                        value = 0
                    eval_formula = re.sub(r'\b' + re.escape(field_name) + r'\b', str(value), eval_formula)
                result = eval(eval_formula)
                return round(result, 2)
            except Exception as e:
                logging.error(f"Error evaluating formula {formula}: {str(e)}")
                return 0.00

        # Prepare per_day and per_part records
        per_day_records = []
        per_part_records = []
        for worker in workers:
            attendance_records = Attendance.query.filter(
                Attendance.worker_id == worker.id,
                Attendance.company_id == company.id,
                Attendance.date.between(start_date, end_date)
            ).all()
            per_day_attendance = {}
            per_part_units = {}
            for att in attendance_records:
                if att.task and getattr(att.task, 'payment_type', None) == 'per_day':
                    if att.status == 'Present':
                        per_day_attendance.setdefault(att.task_id, 0)
                        per_day_attendance[att.task_id] += 1
                elif att.task and getattr(att.task, 'payment_type', None) == 'per_part':
                    if att.units_completed:
                        per_part_units.setdefault(att.task_id, 0)
                        per_part_units[att.task_id] += att.units_completed
            # Only add records if there is actual attendance or units completed in the range
            if per_day_attendance:
                for task_id, days in per_day_attendance.items():
                    task = Task.query.get(task_id) if task_id else None
                    # Compute age
                    try:
                        from datetime import date
                        if worker.date_of_birth:
                            today = date.today()
                            age = today.year - worker.date_of_birth.year - ((today.month, today.day) < (worker.date_of_birth.month, worker.date_of_birth.day))
                        else:
                            age = 0
                    except Exception:
                        age = 0
                    row = {
                        'First Name': getattr(worker, 'first_name', ''),
                        'Last Name': getattr(worker, 'last_name', ''),
                        'Task Name': getattr(task, 'name', '') if task else '',
                        'Attendance Days': days,
                        'Daily Rate': getattr(company, 'daily_payout_rate', None),
                        'age': age,
                    }
                    for field in import_fields:
                        custom_value = WorkerCustomFieldValue.query.filter_by(
                            worker_id=worker.id,
                            custom_field_id=field.id
                        ).first()
                        row[field.name] = custom_value.value if custom_value else 'N/A'
                    # Only add relevant custom fields
                    custom_fields_dict = {field.name: field.formula for field in relevant_custom_fields if field.field_type == 'numeric'}
                    for field in relevant_custom_fields:
                        if field.field_type == 'numeric':
                            try:
                                context = {
                                    'attendance_days': days,
                                    'daily_rate': getattr(company, 'daily_payout_rate', None),
                                    **row
                                }
                                result = evaluate_formula(field.formula, context, custom_fields_dict)
                                if field.max_limit is not None:
                                    result = min(result, field.max_limit)
                                row[field.name] = result
                            except Exception as e:
                                logging.error(f"Error calculating field {field.name}: {str(e)}")
                                row[field.name] = 0.00
                    per_day_records.append(row)
            if per_part_units:
                for task_id, units in per_part_units.items():
                    task = Task.query.get(task_id) if task_id else None
                    # Compute age
                    try:
                        from datetime import date
                        if worker.date_of_birth:
                            today = date.today()
                            age = today.year - worker.date_of_birth.year - ((today.month, today.day) < (worker.date_of_birth.month, worker.date_of_birth.day))
                        else:
                            age = 0
                    except Exception:
                        age = 0
                    row = {
                        'First Name': getattr(worker, 'first_name', ''),
                        'Last Name': getattr(worker, 'last_name', ''),
                        'Task Name': getattr(task, 'name', '') if task else '',
                        'Units Completed': units,
                        'Per Part Rate': getattr(task, 'per_part_payout', None) if task else None,
                        'Per Part Currency': getattr(task, 'per_part_currency', None) if task else None,
                        'age': age,
                    }
                    for field in import_fields:
                        custom_value = WorkerCustomFieldValue.query.filter_by(
                            worker_id=worker.id,
                            custom_field_id=field.id
                        ).first()
                        row[field.name] = custom_value.value if custom_value else 'N/A'
                    # Add custom report fields for per_part
                    per_part_custom_fields = [f for f in custom_fields if f.payout_type in ('per_part', 'both')]
                    custom_fields_dict = {field.name: field.formula for field in per_part_custom_fields if field.field_type == 'numeric'}
                    for field in per_part_custom_fields:
                        if field.field_type == 'numeric':
                            try:
                                context = {
                                    'units_completed': units,
                                    'per_part_rate': row['Per Part Rate'],
                                    **row
                                }
                                result = evaluate_formula(field.formula, context, custom_fields_dict)
                                if field.max_limit is not None:
                                    result = min(result, field.max_limit)
                                row[field.name] = result
                            except Exception as e:
                                logging.error(f"Error calculating field {field.name}: {str(e)}")
                                row[field.name] = 0.00
                    per_part_records.append(row)
        # Create Excel file with two sheets
        import pandas as pd
        import io
        output = io.BytesIO()
        # Check for empty report
        if (report_type == 'per_day' and len(per_day_records) == 0) or (report_type == 'per_part' and len(per_part_records) == 0) or (not report_type and len(per_day_records) == 0 and len(per_part_records) == 0):
            return jsonify({'error': "This report is empty. Are you sure you've selected the correct date range?"}), 400
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if report_type == 'per_day':
                df_day = pd.DataFrame(per_day_records)
                # Only include relevant columns (base + import fields + relevant custom fields)
                if per_day_records:
                    base_cols = ['First Name', 'Last Name', 'Task Name', 'Attendance Days', 'Daily Rate']
                    import_cols = [f.name for f in import_fields]
                    custom_cols = [f.name for f in relevant_custom_fields if f.payout_type in ('per_day', 'both')]
                    cols = base_cols + import_cols + custom_cols
                    df_day = df_day.loc[:, [c for c in cols if c in df_day.columns]]
                df_day.to_excel(writer, index=False, sheet_name='Per Day')
            elif report_type == 'per_part':
                df_part = pd.DataFrame(per_part_records)
                if per_part_records:
                    base_cols = ['First Name', 'Last Name', 'Task Name', 'Units Completed', 'Per Part Rate', 'Per Part Currency']
                    import_cols = [f.name for f in import_fields]
                    custom_cols = [f.name for f in relevant_custom_fields if f.payout_type in ('per_part', 'both')]
                    cols = base_cols + import_cols + custom_cols
                    df_part = df_part.loc[:, [c for c in cols if c in df_part.columns]]
                df_part.to_excel(writer, index=False, sheet_name='Per Part')
            else:
                # Both sheets, include all relevant fields
                df_day = pd.DataFrame(per_day_records)
                df_part = pd.DataFrame(per_part_records)
                df_day.to_excel(writer, index=False, sheet_name='Per Day')
                df_part.to_excel(writer, index=False, sheet_name='Per Part')
        output.seek(0)
        from flask import send_file
        from datetime import datetime as dt
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'report_{dt.now().strftime("%Y%m%d")}.xlsx'
        )
    except Exception as e:
        logging.error(f"Error generating report: {str(e)}")
        return jsonify({'error': f"Failed to generate report: {str(e)}"}), 500
        # Calculate attendance days for each worker
        worker_attendance = {}
        attendance_records = Attendance.query.filter(
            Attendance.company_id == company.id,
            Attendance.date.between(start_date, end_date),
            Attendance.status == 'Present'
        ).all()
        
        for record in attendance_records:
            worker_attendance[record.worker_id] = worker_attendance.get(record.worker_id, 0) + 1
        
        # Modify preview records to include attendance days
        # Get custom fields for formula builder
        custom_fields_for_formulas = ReportField.query.filter_by(company_id=company.id).all()
        
        preview_records = []
        recent_attendance = Attendance.query.filter(
            Attendance.company_id == company.id,
            Attendance.date.between(start_date, end_date)
        ).order_by(Attendance.date.desc()).limit(5).all()
        
        for record in recent_attendance:
            preview_records.append({
                'worker_name': f"{record.worker.first_name} {record.worker.last_name}",
                'task_name': record.task.name,
                'date': record.date.strftime('%Y-%m-%d'),
                'status': record.status,
                'daily_rate': company.daily_payout_rate,
                'attendance_days': worker_attendance.get(record.worker.id, 0)
            })
@app.route("/api/report-field", methods=['POST', 'DELETE', 'PUT'])
def manage_report_field():
    try:
        # Get current company from workspace
        company = get_current_company()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
            
        if request.method == 'DELETE':
            field_id = request.args.get('id')
            if not field_id:
                return jsonify({'error': 'Field ID required'}), 400
                
            field = ReportField.query.filter_by(id=field_id, company_id=company.id).first()
            if not field:
                return jsonify({'error': 'Field not found'}), 404
                
            db.session.delete(field)
            db.session.commit()
            return jsonify({'message': 'Field deleted successfully'}), 200
            
        data = request.get_json()
        
        if request.method == 'PUT':
            field_id = request.args.get('id')
            if not field_id:
                return jsonify({'error': 'Field ID required'}), 400
            try:
                field_id = int(field_id)
            except Exception as e:
                logging.error(f"Invalid field_id: {field_id}, error: {e}")
                return jsonify({'error': 'Invalid field ID'}), 400
            field = ReportField.query.filter_by(id=field_id, company_id=company.id).first()
            if not field:
                return jsonify({'error': 'Field not found'}), 404
            # Exclude current field from duplicate name check
            duplicate = ReportField.query.filter(db.func.lower(ReportField.name) == data['name'].lower(), ReportField.company_id == company.id, ReportField.id != field_id).first()
            logging.info(f"PUT /api/report-field: field_id={field_id}, checking for duplicate name={data['name']}, duplicate={duplicate}")
            if duplicate:
                return jsonify({'error': 'A custom field with this name already exists.'}), 400
            field.name = data['name']
            field.formula = data['formula']
            field.max_limit = data.get('max_limit')
            db.session.commit()
            return jsonify({
                'id': field.id,
                'name': field.name,
                'field_type': 'numeric',
                'formula': field.formula,
                'max_limit': field.max_limit
            }), 200
        
        # POST method
        # Check for duplicate field name (case-insensitive)
        existing = ReportField.query.filter(db.func.lower(ReportField.name) == data['name'].lower(), ReportField.company_id == company.id).first()
        if existing:
            return jsonify({'error': 'A custom field with this name already exists.'}), 400
        new_field = ReportField(
            company_id=company.id,
            name=data['name'],
            field_type='numeric',
            formula=data['formula'],
            max_limit=data.get('max_limit'),
            payout_type=data.get('payout_type', 'per_day')
        )
        
        db.session.add(new_field)
        db.session.commit()
        return jsonify({
            'id': new_field.id,
            'name': new_field.name,
            'field_type': 'numeric',
            'formula': new_field.formula,
            'max_limit': new_field.max_limit
        }), 201
        
    except Exception as e:
        logging.error(f"Error managing report field: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to manage report field'}), 500

@app.route("/task/<int:task_id>/units-completed", methods=['GET'])
def task_units_completed_route(task_id):
    try:
        # Get current company from workspace
        company = get_current_company()

        if not company:
            return render_template('task_units_completed.html', task=None, attendance_records=[], workers=[], selected_date=None)

        # Get the specific task
        task = Task.query.filter_by(id=task_id, company_id=company.id).first()
        if not task or task.payment_type != 'per_part':
            return render_template('500.html'), 500

        # Get all available workers for the company for the dropdown
        available_workers = Worker.query.filter_by(company_id=company.id).all()

        # Get selected date from query parameter, default to today
        from datetime import date
        selected_date_str = request.args.get('date')
        if selected_date_str:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        else:
            selected_date = date.today()

        # If selected date is before task start date, show error and do not show units UI
        if selected_date < task.start_date.date():
            return render_template('task_units_completed.html', 
                task=task, 
                attendance_records=[],
                workers=[],
                available_workers=available_workers,
                selected_date=selected_date,
                attendance_date_error="Units cannot be recorded before the task's start date."
            )

        # Get attendance records for the selected date
        attendance_records = Attendance.query.filter(
            Attendance.company_id == company.id,
            Attendance.date == selected_date,
            Attendance.task_id == task.id
        ).all()

        # Create attendance records for assigned workers if they don't exist
        existing_worker_ids = {record.worker_id for record in attendance_records}
        for worker in task.workers:
            if worker.id not in existing_worker_ids:
                new_attendance = Attendance(
                    worker_id=worker.id,
                    company_id=company.id,
                    date=selected_date,
                    status='Absent',
                    task_id=task.id
                )
                db.session.add(new_attendance)
        db.session.commit()

        # Fetch attendance records again to ensure up-to-date list
        attendance_records = Attendance.query.filter(
            Attendance.company_id == company.id,
            Attendance.date == selected_date,
            Attendance.task_id == task.id
        ).all()

        return render_template('task_units_completed.html', 
            task=task, 
            attendance_records=attendance_records,
            workers=task.workers.all(),  # Only show assigned workers
            available_workers=available_workers,  # Pass all available workers for dropdown
            selected_date=selected_date,
            attendance_date_error=None
        )
    except Exception as e:
        logging.error(f"Error fetching units completed: {str(e)}")
        return render_template('500.html'), 500

@app.route('/admin/master-dashboard')
@master_admin_required
def master_dashboard_route():
    """Master Admin Dashboard - Enhanced Platform Overview with Marketing Insights"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import case, and_
        
        # Time periods for calculations
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        
        # 1. Enhanced Platform Summary Stats
        total_workspaces = Workspace.query.count()
        total_users = User.query.count()
        total_workers = Worker.query.count()
        total_tasks = Task.query.count()
        total_companies = Company.query.count()
        
        # Active metrics
        active_users_7d = User.query.filter(User.created_at >= seven_days_ago).count()
        active_users_30d = User.query.filter(User.created_at >= thirty_days_ago).count()
        recent_users = User.query.filter(User.created_at >= seven_days_ago).count()
        recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
        recent_workers = Worker.query.filter(Worker.created_at >= seven_days_ago).count()
        
        # Task metrics this month
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        
        tasks_this_month = Task.query.filter(Task.created_at >= current_month_start).count()
        tasks_last_month = Task.query.filter(
            Task.created_at >= previous_month_start,
            Task.created_at < current_month_start
        ).count()
        
        # Calculate task growth percentage
        task_growth_percent = 0
        if tasks_last_month > 0:
            task_growth_percent = ((tasks_this_month - tasks_last_month) / tasks_last_month) * 100
        elif tasks_this_month > 0:
            task_growth_percent = 100
        
        # 2. Enhanced Workspace Analytics with Business Metrics
        # Get basic workspace data
        enhanced_workspaces_query = db.session.query(
            Workspace,
            func.count(UserWorkspace.id).label('user_count')
        ).outerjoin(UserWorkspace, Workspace.id == UserWorkspace.workspace_id)\
         .group_by(Workspace.id)\
         .order_by(desc(Workspace.created_at))\
         .all()
        
        # Convert to enhanced workspace data with additional metrics
        enhanced_workspaces = []
        most_active_workspace = None
        max_activity_score = 0
        
        for workspace, user_count in enhanced_workspaces_query:
            # Get company for this workspace
            company = Company.query.filter_by(workspace_id=workspace.id).first()
            
            if company:
                # Get worker count
                worker_count = Worker.query.filter_by(company_id=company.id).count()
                workers_this_month = Worker.query.filter(
                    Worker.company_id == company.id,
                    Worker.created_at >= current_month_start
                ).count()
                
                # Get task counts
                task_count = Task.query.filter_by(company_id=company.id).count()
                tasks_this_month = Task.query.filter(
                    Task.company_id == company.id,
                    Task.created_at >= current_month_start
                ).count()
                completed_tasks = Task.query.filter(
                    Task.company_id == company.id,
                    Task.status == 'Completed'
                ).count()
                
                # Get attendance data
                total_attendance_days = Attendance.query.filter(
                    Attendance.company_id == company.id,
                    Attendance.date >= current_month_start,
                    Attendance.status == 'Present'
                ).count()
            else:
                worker_count = 0
                workers_this_month = 0
                task_count = 0
                tasks_this_month = 0
                completed_tasks = 0
                total_attendance_days = 0
            
            activity_score = task_count + worker_count + tasks_this_month
            completion_rate = (completed_tasks / task_count * 100) if task_count > 0 else 0
            
            workspace_info = {
                'workspace': workspace,
                'user_count': user_count,
                'company_count': 1 if company else 0,
                'task_count': task_count,
                'worker_count': worker_count,
                'tasks_this_month': tasks_this_month,
                'workers_this_month': workers_this_month,
                'completed_tasks': completed_tasks,
                'total_attendance_days': total_attendance_days,
                'activity_score': activity_score,
                'completion_rate': completion_rate
            }
            enhanced_workspaces.append(workspace_info)
            
            # Track most active workspace
            if activity_score > max_activity_score:
                max_activity_score = activity_score
                most_active_workspace = workspace_info
        
        # Recent workspaces (top 10 for display)
        recent_workspaces = enhanced_workspaces[:10]
        
        # Industry and country stats
        industry_stats = db.session.query(
            Workspace.industry_type,
            func.count(Workspace.id).label('count')
        ).group_by(Workspace.industry_type).order_by(desc('count')).all()
        
        country_stats = db.session.query(
            Workspace.country,
            func.count(Workspace.id).label('count')
        ).group_by(Workspace.country).order_by(desc('count')).all()
        
        # Top performing workspaces by different metrics
        top_workspaces_by_tasks = sorted(enhanced_workspaces, key=lambda x: x['task_count'], reverse=True)[:5]
        top_workspaces_by_workers = sorted(enhanced_workspaces, key=lambda x: x['worker_count'], reverse=True)[:5]
        top_workspaces_by_activity = sorted(enhanced_workspaces, key=lambda x: x['activity_score'], reverse=True)[:5]
        
        # 3. Enhanced User Analytics
        role_stats = db.session.query(
            UserWorkspace.role,
            func.count(UserWorkspace.id).label('count')
        ).group_by(UserWorkspace.role).all()
        
        # User engagement metrics
        all_users_data = db.session.query(
            User,
            func.count(UserWorkspace.id).label('workspace_count')
        ).outerjoin(UserWorkspace, User.id == UserWorkspace.user_id)\
         .group_by(User.id)\
         .order_by(desc(User.id))\
         .limit(50).all()
        
        all_users = []
        for user_data in all_users_data:
            user, workspace_count = user_data
            # Get user roles
            user_roles = db.session.query(UserWorkspace.role).filter_by(user_id=user.id).distinct().all()
            roles = [role[0] for role in user_roles] if user_roles else []
            
            all_users.append({
                'user': user,
                'workspace_count': workspace_count,
                'roles': roles
            })
        
        # User growth data (last 30 days)
        user_growth_data = []
        task_growth_data = []
        for i in range(30):
            date = datetime.utcnow() - timedelta(days=i)
            user_count = User.query.filter(
                func.date(User.created_at) == date.date()
            ).count()
            task_count = Task.query.filter(
                func.date(Task.created_at) == date.date()
            ).count()
            user_growth_data.append((date.strftime('%m-%d'), user_count))
            task_growth_data.append((date.strftime('%m-%d'), task_count))
        user_growth_data.reverse()
        task_growth_data.reverse()
        
        # 4. Enhanced Subscription & Revenue Analytics
        subscription_stats = db.session.query(
            Workspace.subscription_status,
            func.count(Workspace.id).label('count')
        ).group_by(Workspace.subscription_status).all()
        
        active_subscriptions = sum(count for status, count in subscription_stats if status == 'active')
        free_trials = sum(count for status, count in subscription_stats if status == 'trial')
        failed_payments = sum(count for status, count in subscription_stats if status == 'past_due')
        
        # Enhanced revenue calculation
        estimated_revenue = active_subscriptions * 29.99
        
        # Expiring trials (next 7 days)
        expiring_trials = Workspace.query.filter(
            Workspace.trial_end_date <= datetime.utcnow() + timedelta(days=7),
            Workspace.subscription_status == 'trial'
        ).all()
        
        # 5. Marketing Analytics & Business Intelligence
        marketing_data = {
            'conversion_metrics': {
                'total_signups': total_workspaces,
                'paid_workspaces': active_subscriptions,
                'trial_workspaces': free_trials,
                'conversion_rate': round((active_subscriptions / total_workspaces * 100) if total_workspaces > 0 else 0, 1)
            },
            'geographic_data': [(country, count, 0, 0) for country, count in country_stats[:10]],
            'industry_performance': [],
            'growth_data': [],
            'market_opportunities': [],
            'industry_opportunities': []
        }
        
        # Industry performance analysis
        for industry, workspace_count in industry_stats:
            if workspace_count > 0:
                paid_in_industry = db.session.query(func.count(Workspace.id)).filter(
                    Workspace.industry_type == industry,
                    Workspace.subscription_status == 'active'
                ).scalar()
                
                marketing_data['industry_performance'].append((
                    industry, workspace_count, 0, paid_in_industry, 0
                ))
        
        # Growth trend data (last 6 months)
        for i in range(6):
            month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            signups = Workspace.query.filter(
                Workspace.created_at >= month_start,
                Workspace.created_at < month_end
            ).count()
            
            conversions = Workspace.query.filter(
                Workspace.created_at >= month_start,
                Workspace.created_at < month_end,
                Workspace.subscription_status == 'active'
            ).count()
            
            marketing_data['growth_data'].append({
                'month': month_start.strftime('%Y-%m'),
                'signups': signups,
                'conversions': conversions,
                'conversion_rate': (conversions / signups * 100) if signups > 0 else 0
            })
        
        marketing_data['growth_data'].reverse()
        
        # Market opportunities (top countries with growth potential)
        for country, count in country_stats[:5]:
            potential_revenue = count * 29.99  # Assuming conversion
            marketing_data['market_opportunities'].append({
                'country': country,
                'workspace_count': count,
                'potential_revenue': potential_revenue
            })
        
        # Industry opportunities (best conversion rates)
        industry_conversions = []
        for industry, workspace_count in industry_stats:
            if workspace_count >= 3:  # Only consider industries with meaningful data
                paid_count = db.session.query(func.count(Workspace.id)).filter(
                    Workspace.industry_type == industry,
                    Workspace.subscription_status == 'active'
                ).scalar()
                
                conversion_rate = (paid_count / workspace_count * 100) if workspace_count > 0 else 0
                industry_conversions.append({
                    'industry': industry,
                    'workspace_count': workspace_count,
                    'conversion_rate': conversion_rate
                })
        
        marketing_data['industry_opportunities'] = sorted(
            industry_conversions, key=lambda x: x['conversion_rate'], reverse=True
        )[:3]
        
        marketing_data['active_users_30d'] = active_users_30d
        
        # 6. Business Health Metrics
        inactive_workspaces = sum(1 for ws in enhanced_workspaces if ws['tasks_this_month'] == 0)
        high_activity_workspaces = sum(1 for ws in enhanced_workspaces if ws['activity_score'] > 10)
        
        # 7. Enhanced Alerts & Notifications
        alerts = []
        
        if expiring_trials:
            alerts.append({
                'type': 'warning',
                'message': f'{len(expiring_trials)} workspaces have expiring trials in the next 7 days'
            })
        
        if failed_payments > 0:
            alerts.append({
                'type': 'error',
                'message': f'{failed_payments} workspaces have failed payments'
            })
        
        if inactive_workspaces > 0:
            alerts.append({
                'type': 'info',
                'message': f'{inactive_workspaces} workspaces have no tasks created this month'
            })
        
        # 8. Top Performing Metrics for Marketing
        top_workspaces = sorted(enhanced_workspaces, key=lambda x: x['task_count'], reverse=True)[:5]
        
        # Additional master admin stats
        master_admins_count = MasterAdmin.query.filter_by(is_active=True).count()
        
        # 9. Enhanced Task Analytics with Worker Counts
        # Get tasks with most workers (through Task-Worker relationships)
        task_worker_analytics = []
        
        # Query tasks with worker counts from attendance records
        task_worker_counts = db.session.query(
            Task.id,
            Task.name,
            Task.payment_type,
            Task.status,
            Task.created_at,
            Company.name.label('company_name'),
            Workspace.name.label('workspace_name'),
            func.count(func.distinct(Attendance.worker_id)).label('unique_workers'),
            func.count(Attendance.id).label('total_attendance'),
            func.avg(case(
                (Attendance.units_completed.isnot(None), Attendance.units_completed),
                else_=0
            )).label('avg_units_completed')
        ).join(Company, Task.company_id == Company.id)\
         .join(Workspace, Company.workspace_id == Workspace.id)\
         .outerjoin(Attendance, Task.id == Attendance.task_id)\
         .group_by(Task.id, Task.name, Task.payment_type, Task.status, Task.created_at, Company.name, Workspace.name)\
         .order_by(desc('unique_workers'), desc('total_attendance'))\
         .limit(20).all()
        
        for task_data in task_worker_counts:
            task_id, task_name, payment_type, status, created_at, company_name, workspace_name, unique_workers, total_attendance, avg_units = task_data
            
            # Calculate task priority based on worker engagement and completion
            if unique_workers >= 10:
                priority = 'high'
            elif unique_workers >= 5:
                priority = 'medium'
            else:
                priority = 'low'
            
            # Calculate task efficiency metrics
            efficiency_score = 0
            if total_attendance > 0 and avg_units:
                efficiency_score = round(float(avg_units) * unique_workers / total_attendance * 100, 1)
            
            task_worker_analytics.append({
                'task_id': task_id,
                'task_name': task_name,
                'payment_type': payment_type,
                'status': status,
                'created_at': created_at,
                'company_name': company_name,
                'workspace_name': workspace_name,
                'unique_workers': unique_workers or 0,
                'total_attendance': total_attendance or 0,
                'avg_units_completed': round(float(avg_units), 2) if avg_units else 0,
                'priority': priority,
                'efficiency_score': efficiency_score
            })
        
        # Top tasks by different metrics
        top_tasks_by_workers = sorted(task_worker_analytics, key=lambda x: x['unique_workers'], reverse=True)[:10]
        top_tasks_by_attendance = sorted(task_worker_analytics, key=lambda x: x['total_attendance'], reverse=True)[:10]
        top_tasks_by_efficiency = sorted(task_worker_analytics, key=lambda x: x['efficiency_score'], reverse=True)[:10]
        
        # Task completion analytics
        completed_tasks_with_workers = [t for t in task_worker_analytics if t['status'] == 'Completed']
        active_tasks_with_workers = [t for t in task_worker_analytics if t['status'] in ['Active', 'In Progress']]
        
        # Payment type distribution for high-worker tasks
        payment_type_analytics = {}
        for task in task_worker_analytics:
            ptype = task['payment_type'] or 'Not Set'
            if ptype not in payment_type_analytics:
                payment_type_analytics[ptype] = {
                    'count': 0,
                    'total_workers': 0,
                    'avg_workers': 0
                }
            payment_type_analytics[ptype]['count'] += 1
            payment_type_analytics[ptype]['total_workers'] += task['unique_workers']
        
        # Calculate averages
        for ptype in payment_type_analytics:
            if payment_type_analytics[ptype]['count'] > 0:
                payment_type_analytics[ptype]['avg_workers'] = round(
                    payment_type_analytics[ptype]['total_workers'] / payment_type_analytics[ptype]['count'], 1
                )
        
        # Monthly task trends with worker engagement
        monthly_task_trends = []
        for i in range(12):
            month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            tasks_created = Task.query.filter(
                Task.created_at >= month_start,
                Task.created_at < month_end
            ).count()
            
            # Get worker engagement for tasks created in this month
            worker_engagement = db.session.query(
                func.count(func.distinct(Attendance.worker_id))
            ).join(Task, Attendance.task_id == Task.id)\
             .filter(
                Task.created_at >= month_start,
                Task.created_at < month_end
            ).scalar() or 0
            
            monthly_task_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'tasks_created': tasks_created,
                'worker_engagement': worker_engagement,
                'avg_workers_per_task': round(worker_engagement / tasks_created, 1) if tasks_created > 0 else 0
            })
        
        monthly_task_trends.reverse()
        
        return render_template('admin/master_dashboard.html',
                             # Enhanced Platform Summary
                             total_workspaces=total_workspaces,
                             total_users=total_users,
                             total_companies=total_companies,
                             active_users_7d=active_users_7d,
                             active_users_30d=active_users_30d,
                             total_workers=total_workers,
                             total_tasks=total_tasks,
                             tasks_this_month=tasks_this_month,
                             task_growth_percent=task_growth_percent,
                             recent_users=recent_users,
                             recent_tasks=recent_tasks,
                             recent_workers=recent_workers,
                             
                             # Enhanced Workspace Analytics
                             industry_stats=industry_stats,
                             country_stats=country_stats,
                             recent_workspaces=recent_workspaces,
                             enhanced_workspaces=enhanced_workspaces[:20],  # Limit for display
                             most_active_workspace=most_active_workspace,
                             top_workspaces_by_tasks=top_workspaces_by_tasks,
                             top_workspaces_by_workers=top_workspaces_by_workers,
                             top_workspaces_by_activity=top_workspaces_by_activity,
                             inactive_workspaces=inactive_workspaces,
                             high_activity_workspaces=high_activity_workspaces,
                             
                             # Enhanced User Analytics
                             role_stats=role_stats,
                             user_growth_data=user_growth_data,
                             task_growth_data=task_growth_data,
                             all_users=all_users,
                             
                             # Enhanced Subscription & Revenue
                             subscription_stats=subscription_stats,
                             active_subscriptions=active_subscriptions,
                             free_trials=free_trials,
                             failed_payments=failed_payments,
                             estimated_revenue=estimated_revenue,
                             expiring_trials=expiring_trials,
                             
                             # Marketing Analytics
                             marketing_data=marketing_data,
                             
                             # Top Performing Metrics
                             top_workspaces=top_workspaces,
                             
                             # Management
                             master_admins_count=master_admins_count,
                             
                             # Enhanced Task Analytics
                             task_worker_analytics=task_worker_analytics,
                             top_tasks_by_workers=top_tasks_by_workers,
                             top_tasks_by_attendance=top_tasks_by_attendance,
                             top_tasks_by_efficiency=top_tasks_by_efficiency,
                             completed_tasks_with_workers=completed_tasks_with_workers,
                             active_tasks_with_workers=active_tasks_with_workers,
                             payment_type_analytics=payment_type_analytics,
                             monthly_task_trends=monthly_task_trends,
                             
                             # Alerts
                             alerts=alerts,
                             
                             # Current time for calculations
                             now=datetime.utcnow())
    except Exception as e:
        logging.error(f"Error in master dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('500.html'), 500

@app.route('/admin/user-growth-data/<period>')
@master_admin_required
def user_growth_data_route(period):
    try:
        # Determine the number of days and format based on period
        if period == '7d':
            days = 7
            date_format = '%m-%d'
        elif period == '30d':
            days = 30
            date_format = '%m-%d'
        elif period == '1y':
            days = 365
            date_format = '%Y-%m'  # Group by month for yearly view
        else:
            return jsonify({'error': 'Invalid period'}), 400
        
        user_growth_data = []
        
        if period == '1y':
            # For yearly view, group by month
            for i in range(12):
                start_date = datetime.utcnow().replace(day=1) - timedelta(days=30 * i)
                end_date = start_date.replace(day=1) + timedelta(days=32)
                end_date = end_date.replace(day=1) - timedelta(days=1)  # Last day of month
                
                user_count = User.query.filter(
                    func.date(User.created_at) >= start_date.date(),
                    func.date(User.created_at) <= end_date.date()
                ).count()
                
                user_growth_data.append({
                    'label': start_date.strftime('%Y-%m'),
                    'count': user_count
                })
            user_growth_data.reverse()
        else:
            # For daily view (7d and 30d)
            for i in range(days):
                date = datetime.utcnow() - timedelta(days=i)
                user_count = User.query.filter(
                    func.date(User.created_at) == date.date()
                ).count()
                user_growth_data.append({
                    'label': date.strftime(date_format),
                    'count': user_count
                })
            user_growth_data.reverse()
        
        return jsonify({
            'success': True,
            'data': user_growth_data
        })
        
    except Exception as e:
        logging.error(f"Error fetching user growth data: {str(e)}")
        return jsonify({'error': f'Error fetching data: {str(e)}'}), 500

@app.route('/admin/pause-workspace/<int:workspace_id>', methods=['POST'])
@master_admin_required
def pause_workspace_route(workspace_id):
    try:
        workspace = Workspace.query.get(workspace_id)
        if not workspace:
            return jsonify({'error': 'Workspace not found'}), 404
        
        # Store original subscription status and set to paused
        if workspace.subscription_status != 'paused':
            # We'll use 'paused' as a special status
            workspace.subscription_status = 'paused'
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Workspace "{workspace.name}" has been paused',
                'status': 'paused'
            })
        else:
            return jsonify({'error': 'Workspace is already paused'}), 400
            
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error pausing workspace: {str(e)}")
        return jsonify({'error': f'Error pausing workspace: {str(e)}'}), 500

@app.route('/admin/resume-workspace/<int:workspace_id>', methods=['POST'])
@master_admin_required
def resume_workspace_route(workspace_id):
    try:
        workspace = Workspace.query.get(workspace_id)
        if not workspace:
            return jsonify({'error': 'Workspace not found'}), 404
        
        if workspace.subscription_status == 'paused':
            # Resume with appropriate status based on subscription dates
            from datetime import datetime
            now = datetime.utcnow()
            
            if workspace.subscription_end_date and workspace.subscription_end_date > now:
                workspace.subscription_status = 'active'
            elif workspace.trial_end_date and workspace.trial_end_date > now:
                workspace.subscription_status = 'trial'
            else:
                workspace.subscription_status = 'expired'
                
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Workspace "{workspace.name}" has been resumed',
                'status': workspace.subscription_status
            })
        else:
            return jsonify({'error': 'Workspace is not paused'}), 400
            
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error resuming workspace: {str(e)}")
        return jsonify({'error': f'Error resuming workspace: {str(e)}'}), 500

@app.route('/admin/delete-workspace/<int:workspace_id>', methods=['POST'])
@master_admin_required
def delete_workspace_route(workspace_id):
    try:
        workspace = Workspace.query.get(workspace_id)
        if not workspace:
            return jsonify({'error': 'Workspace not found'}), 404
        
        # With proper cascade relationships, we can simply delete the workspace
        # and all related data will be automatically deleted
        db.session.delete(workspace)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting workspace: {str(e)}")
        return jsonify({'error': f'Error deleting workspace: {str(e)}'}), 500

@app.route('/admin/delete-worker/<int:worker_id>', methods=['POST'])
@master_admin_required
def delete_worker_route(worker_id):
    try:
        worker = Worker.query.get(worker_id)
        if not worker:
            return jsonify({'error': 'Worker not found'}), 404
        db.session.delete(worker)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/master-admins')
@master_admin_required
def master_admins_route():
    """Master Admins Management Page"""
    try:
        master_admins = MasterAdmin.query.filter_by(is_active=True).all()
        return render_template('admin/master_admins.html', master_admins=master_admins)
    except Exception as e:
        logging.error(f"Error in master admins route: {str(e)}")
        return render_template('500.html'), 500

@app.route('/admin/add-master-admin', methods=['POST'])
@master_admin_required
def add_master_admin_route():
    """Add a new master admin"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        name = data.get('name', '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Check if email already exists
        existing_admin = MasterAdmin.query.filter_by(email=email).first()
        if existing_admin:
            return jsonify({'error': 'Email already exists'}), 400
        
        # Get current master admin
        current_admin = MasterAdmin.query.filter_by(email=session['user']['user_email']).first()
        
        new_master_admin = MasterAdmin(
            email=email,
            name=name,
            created_by=current_admin.id if current_admin else None
        )
        
        db.session.add(new_master_admin)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Master admin added successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding master admin: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/delete-master-admin/<int:admin_id>', methods=['POST'])
@master_admin_required
def delete_master_admin_route(admin_id):
    """Delete a master admin (soft delete)"""
    try:
        master_admin = MasterAdmin.query.get(admin_id)
        if not master_admin:
            return jsonify({'error': 'Master admin not found'}), 404
        
        # Don't allow self-deletion
        if master_admin.email == session['user']['user_email']:
            return jsonify({'error': 'Cannot delete yourself'}), 400
        
        master_admin.is_active = False
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@master_admin_required
def delete_user_route(user_id):
    """Delete a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/export/workspaces')
@master_admin_required
def export_workspaces_route():
    """Export workspaces to CSV"""
    try:
        import csv
        from io import StringIO
        from datetime import datetime
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Name', 'Country', 'Industry', 'Workspace Code', 'Subscription Status', 'Created At', 'User Count'])
        
        # Get all workspaces with user counts
        workspaces = db.session.query(
            Workspace,
            func.count(UserWorkspace.id).label('user_count')
        ).outerjoin(UserWorkspace, Workspace.id == UserWorkspace.workspace_id)\
         .group_by(Workspace.id)\
         .all()
        
        for workspace, user_count in workspaces:
            writer.writerow([
                workspace.id,
                workspace.name,
                workspace.country,
                workspace.industry_type,
                workspace.workspace_code,
                workspace.subscription_status,
                workspace.created_at.strftime('%Y-%m-%d'),
                user_count
            ])
        
        output.seek(0)
        return send_file(
            StringIO(output.getvalue()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'workspaces_export_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        )
    except Exception as e:
        logging.error(f"Error exporting workspaces: {str(e)}")
        return jsonify({'error': 'Failed to export workspaces'}), 500

@app.route('/admin/export/users')
@master_admin_required
def export_users_route():
    """Export users to CSV"""
    try:
        import csv
        from io import StringIO
        from datetime import datetime
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Email', 'Profile Picture', 'Role', 'Created At'])
        
        users = User.query.all()
        for user in users:
            writer.writerow([
                user.id,
                user.email,
                user.profile_picture or '',
                user.role,
                user.created_at.strftime('%Y-%m-%d') if hasattr(user, 'created_at') else ''
            ])
        
        output.seek(0)
        return send_file(
            StringIO(output.getvalue()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'users_export_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        )
    except Exception as e:
        logging.error(f"Error exporting users: {str(e)}")
        return jsonify({'error': 'Failed to export users'}), 500

@app.route('/admin/export/revenue')
@master_admin_required
def export_revenue_route():
    """Export revenue report to CSV"""
    try:
        import csv
        from io import StringIO
        from datetime import datetime
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Workspace', 'Country', 'Industry', 'Subscription Status', 'Trial End Date', 'Estimated Revenue'])
        
        workspaces = Workspace.query.all()
        for workspace in workspaces:
            revenue = 29.99 if workspace.subscription_status == 'active' else 0
            writer.writerow([
                workspace.name,
                workspace.country,
                workspace.industry_type,
                workspace.subscription_status,
                workspace.trial_end_date.strftime('%Y-%m-%d') if workspace.trial_end_date else '',
                f"${revenue:.2f}"
            ])
        
        output.seek(0)
        return send_file(
            StringIO(output.getvalue()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'revenue_report_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        )
    except Exception as e:
        logging.error(f"Error exporting revenue: {str(e)}")
        return jsonify({'error': 'Failed to export revenue report'}), 500

@app.route('/admin/debug-master-dashboard')
def debug_master_dashboard():
    """Debug route to check master dashboard data and authentication"""
    try:
        from datetime import datetime, timedelta
        
        # Check authentication
        auth_status = {
            'session_exists': 'user' in session,
            'user_email': session.get('user', {}).get('user_email') if 'user' in session else None,
            'is_master_admin': False
        }
        
        # Check if user is master admin
        if 'user' in session and 'user_email' in session['user']:
            from models import MasterAdmin
            master_admin = MasterAdmin.query.filter_by(
                email=session['user']['user_email'], 
                is_active=True
            ).first()
            auth_status['is_master_admin'] = bool(master_admin)
            auth_status['master_admin_record'] = master_admin.to_dict() if master_admin else None
        
        # Get basic counts
        counts = {
            'total_workspaces': Workspace.query.count(),
            'total_users': User.query.count(),
            'total_workers': Worker.query.count(),
            'total_tasks': Task.query.count(),
            'total_master_admins': MasterAdmin.query.count()
        }
        
        # Get sample data
        sample_data = {
            'recent_workspaces': [w.to_dict() for w in Workspace.query.order_by(Workspace.created_at.desc()).limit(5).all()],
            'recent_users': [u.to_dict() for u in User.query.order_by(User.created_at.desc()).limit(5).all()],
            'master_admins': [ma.to_dict() for ma in MasterAdmin.query.all()]
        }
        
        return jsonify({
            'auth_status': auth_status,
            'counts': counts,
            'sample_data': sample_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/admin/create-master-admin-debug', methods=['POST'])
def create_master_admin_debug():
    """Debug route to create a master admin"""
    try:
        from models import MasterAdmin
        
        # Get email from request
        data = request.get_json()
        email = data.get('email', 'markbmwape@gmail.com')
        name = data.get('name', 'Master Admin')
        
        # Check if master admin already exists
        existing = MasterAdmin.query.filter_by(email=email).first()
        if existing:
            return jsonify({
                'message': 'Master admin already exists',
                'master_admin': existing.to_dict()
            })
        
        # Create new master admin
        master_admin = MasterAdmin(
            email=email,
            name=name,
            is_active=True
        )
        db.session.add(master_admin)
        db.session.commit()
        
        return jsonify({
            'message': 'Master admin created successfully',
            'master_admin': master_admin.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500