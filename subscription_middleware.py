from functools import wraps
from flask import session, jsonify, request, redirect, url_for, render_template
from datetime import datetime
from models import Workspace, UserWorkspace, User, db
import logging

def subscription_required(f):
    """Decorator to check if user has valid subscription or trial"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip check for API routes and certain endpoints
        excluded_endpoints = [
            'static', 'landing_route', 'signin_route', 'finish_signin_route',
            'set_session', 'logout_route', 'signout', 'workspace_selection_route',
            'create_workspace', 'join_workspace', 'get_workspace_payments',
            'terms_of_use_route', 'privacy_policy_route', 'legal_compliance_route'
        ]
        
        if request.endpoint in excluded_endpoints:
            return f(*args, **kwargs)
        
        # Check if user is authenticated
        if 'user' not in session or 'current_workspace' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('signin_route'))
        
        try:
            workspace_id = session['current_workspace']['id']
            workspace = Workspace.query.get(workspace_id)
            
            if not workspace:
                if request.is_json:
                    return jsonify({'error': 'Workspace not found'}), 404
                return redirect(url_for('workspace_selection_route'))
            
            # Check subscription status
            subscription_status = check_subscription_status(workspace)
            
            if subscription_status == 'expired':
                # Trial has expired and no active subscription
                if request.is_json:
                    return jsonify({
                        'error': 'Subscription required',
                        'trial_expired': True,
                        'message': 'Your free trial has expired. Please upgrade to continue using the service.'
                    }), 402  # Payment Required
                
                # For regular requests, show upgrade page
                return render_template('subscription_required.html', workspace=workspace)
            
            elif subscription_status == 'trial_expiring':
                # Trial is expiring soon (1 day or less)
                # Allow access but show warning
                pass
            
            # Continue with normal request
            return f(*args, **kwargs)
            
        except Exception as e:
            logging.error(f"Error checking subscription: {str(e)}")
            return f(*args, **kwargs)  # Allow access on error to avoid breaking the app
    
    return decorated_function

def check_subscription_status(workspace):
    """Check the subscription status of a workspace"""
    now = datetime.utcnow()
    
    # Check if they have an active Stripe subscription
    if workspace.stripe_subscription_id and workspace.subscription_status == 'active':
        if workspace.subscription_end_date and workspace.subscription_end_date > now:
            return 'active'
    
    # Check trial status
    if workspace.trial_end_date:
        days_left = (workspace.trial_end_date - now).days
        
        if days_left > 1:
            return 'trial_active'
        elif days_left >= 0:
            return 'trial_expiring'  # Last day
        else:
            # Trial has expired, check if they have a subscription
            if workspace.stripe_subscription_id:
                return 'active'  # They have a subscription even if trial expired
            else:
                return 'expired'  # Trial expired and no subscription
    
    # Default case - no trial end date set, assume active for now
    return 'trial_active'

def is_paid_user(workspace):
    """Check if a workspace belongs to a paid user"""
    now = datetime.utcnow()
    
    # Check if they have an active subscription
    if workspace.subscription_status == 'active' and workspace.stripe_subscription_id:
        return True
    
    # Check if subscription is still valid
    if workspace.subscription_end_date and workspace.subscription_end_date > now:
        return True
    
    # If trial has ended and they have a subscription
    if (workspace.trial_end_date and 
        workspace.trial_end_date < now and 
        workspace.stripe_subscription_id):
        return True
    
    return False

def admin_required(f):
    """Decorator to check if user is admin in current workspace"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'current_workspace' not in session:
            if request.is_json:
                return jsonify({'error': 'No active workspace'}), 400
            return redirect(url_for('workspace_selection_route'))
        
        user_role = session['current_workspace'].get('role')
        if user_role != 'Admin':
            if request.is_json:
                return jsonify({'error': 'Admin access required'}), 403
            return render_template('403.html'), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
