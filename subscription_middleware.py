from functools import wraps
from flask import session, jsonify, request, redirect, url_for, render_template
from datetime import datetime
from models import Workspace, UserWorkspace, User, db, Worker
from tier_config import get_tier_spec, validate_tier_access, get_worker_limit, has_feature
import logging

def subscription_required(f):
    """Decorator to check if user has valid subscription or trial"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip check for API routes and certain endpoints
        excluded_endpoints = [
            'static', 'landing_route', 'signin_route', 'finish_signin_route',
            'set_session', 'logout_route', 'signout',
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
                return redirect(url_for('signin_route'))
            
            # Check subscription status
            subscription_status = check_subscription_status(workspace)
            
            if subscription_status == 'expired':
                # Trial has expired and no active subscription OR subscription canceled/failed
                if request.is_json:
                    return jsonify({
                        'error': 'Subscription required',
                        'trial_expired': True,
                        'message': 'Your subscription has expired. Please renew to continue using the service.'
                    }), 402  # Payment Required
                
                # For regular requests, show upgrade page
                return render_template('subscription_required.html', workspace=workspace)
            
            elif subscription_status == 'past_due':
                # Payment failed - give 3-day grace period
                if workspace.subscription_end_date:
                    days_since_due = (datetime.utcnow() - workspace.subscription_end_date).days
                    if days_since_due > 3:  # Grace period expired
                        if request.is_json:
                            return jsonify({
                                'error': 'Payment overdue',
                                'payment_failed': True,
                                'message': 'Your payment has failed. Please update your payment method.'
                            }), 402  # Payment Required
                        
                        return render_template('subscription_required.html', workspace=workspace)
                    # Still in grace period - allow access but show warning
                
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
    
    # Check subscription status from Stripe webhooks
    if workspace.stripe_subscription_id:
        if workspace.subscription_status == 'active':
            # Check if subscription end date has passed
            if workspace.subscription_end_date and workspace.subscription_end_date > now:
                return 'active'
            else:
                return 'expired'  # Subscription end date has passed
        elif workspace.subscription_status == 'past_due':
            return 'past_due'  # Failed payment - give grace period
        elif workspace.subscription_status == 'canceled':
            return 'expired'  # Subscription was canceled
        elif workspace.subscription_status in ['unpaid', 'incomplete']:
            return 'expired'  # Payment issues
    
    # Check trial status (for users without paid subscriptions)
    if workspace.trial_end_date:
        days_left = (workspace.trial_end_date - now).days
        
        if days_left > 1:
            return 'trial_active'
        elif days_left >= 0:
            return 'trial_expiring'  # Last day
        else:
            return 'expired'  # Trial expired and no active subscription
    
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
            return redirect(url_for('signin_route'))
        
        user_role = session['current_workspace'].get('role')
        if user_role != 'Admin':
            if request.is_json:
                return jsonify({'error': 'Admin access required'}), 403
            return render_template('403.html'), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def feature_required(feature_name):
    """Decorator to check if current tier has access to specific feature"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'current_workspace' not in session:
                if request.is_json:
                    return jsonify({'error': 'No active workspace'}), 400
                return redirect(url_for('signin_route'))
            
            try:
                workspace_id = session['current_workspace']['id']
                workspace = Workspace.query.get(workspace_id)
                
                if not workspace:
                    if request.is_json:
                        return jsonify({'error': 'Workspace not found'}), 404
                    return redirect(url_for('signin_route'))
                
                # Check if tier has this feature
                is_allowed, reason = validate_tier_access(workspace, feature_name=feature_name)
                
                if not is_allowed:
                    if request.is_json:
                        return jsonify({
                            'error': 'Feature not available',
                            'message': reason,
                            'upgrade_required': True
                        }), 403
                    
                    # Render upgrade page with feature info
                    tier_spec = get_tier_spec(workspace.subscription_tier or 'starter')
                    return render_template('feature_upgrade_required.html', 
                                         workspace=workspace,
                                         feature_name=feature_name,
                                         current_tier=tier_spec,
                                         reason=reason)
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logging.error(f"Error checking feature access: {str(e)}")
                db.session.rollback()  # Rollback failed transaction
                return f(*args, **kwargs)  # Allow access on error
        
        return decorated_function
    return decorator

def worker_limit_check(f):
    """Decorator to check worker limits before adding new workers"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'current_workspace' not in session:
            return f(*args, **kwargs)  # Let other middleware handle auth
        
        try:
            workspace_id = session['current_workspace']['id']
            workspace = Workspace.query.get(workspace_id)
            
            if workspace:
                # Get company associated with this workspace
                from models import Company
                company = Company.query.filter_by(workspace_id=workspace_id).first()
                
                if company:
                    # Count current workers for this company
                    current_worker_count = Worker.query.filter_by(company_id=company.id).count()
                    
                    # Check if adding one more would exceed limit
                    is_allowed, reason = validate_tier_access(workspace, worker_count=current_worker_count + 1)
                    
                    if not is_allowed:
                        if request.is_json:
                            return jsonify({
                                'error': 'Worker limit exceeded',
                                'message': reason,
                                'current_count': current_worker_count,
                                'limit': get_worker_limit(workspace.subscription_tier or 'starter'),
                                'upgrade_required': True
                            }), 403
                        
                        # For form submissions, flash message and redirect
                        from flask import flash
                        flash(reason, 'error')
                        return redirect(request.referrer or url_for('home'))
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logging.error(f"Error checking worker limit: {str(e)}")
            db.session.rollback()  # Rollback failed transaction
            return f(*args, **kwargs)  # Allow on error
    
    return decorated_function
