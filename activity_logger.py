import json
from datetime import datetime
from flask import session, request
from models import ActivityLog, db, User
import logging

def log_activity(action_type, resource_type, description, resource_id=None, details=None, user_email=None, workspace_id=None):
    """
    Log user activity in the workspace
    
    Args:
        action_type (str): Type of action ('create', 'update', 'delete', 'import', 'login', 'logout', 'view')
        resource_type (str): Type of resource ('worker', 'task', 'company', 'team_member', 'attendance', 'report', 'workspace')
        description (str): Human-readable description of the action
        resource_id (int, optional): ID of the affected resource
        details (dict, optional): Additional details to store as JSON
        user_email (str, optional): User email (if not in session)
        workspace_id (int, optional): Workspace ID (if not in session)
    """
    try:
        # Get user info from session or parameters
        if not user_email and 'user' in session and 'user_email' in session['user']:
            user_email = session['user']['user_email']
        
        if not workspace_id and 'current_workspace' in session:
            workspace_id = session['current_workspace']['id']
        
        # Skip logging if we don't have required information
        if not user_email or not workspace_id:
            return
        
        # Get user object for user_id
        user = User.query.filter_by(email=user_email).first()
        user_id = user.id if user else None
        
        # Get IP address and User Agent
        ip_address = request.remote_addr if request else None
        user_agent = request.headers.get('User-Agent') if request else None
        
        # Convert details to JSON string if provided
        details_json = json.dumps(details) if details else None
        
        # Create activity log entry
        activity_log = ActivityLog(
            workspace_id=workspace_id,
            user_id=user_id,
            user_email=user_email,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            details=details_json,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(activity_log)
        db.session.commit()
        
        logging.info(f"Activity logged: {action_type} {resource_type} by {user_email}: {description}")
        
    except Exception as e:
        logging.error(f"Failed to log activity: {str(e)}")
        # Don't raise the exception to avoid breaking the main functionality
        db.session.rollback()

def get_recent_activities(workspace_id, limit=50):
    """
    Get recent activities for a workspace
    
    Args:
        workspace_id (int): Workspace ID
        limit (int): Number of activities to retrieve
    
    Returns:
        list: List of activity log entries
    """
    try:
        activities = ActivityLog.query.filter_by(
            workspace_id=workspace_id
        ).order_by(
            ActivityLog.created_at.desc()
        ).limit(limit).all()
        
        return [activity.to_dict() for activity in activities]
    except Exception as e:
        logging.error(f"Failed to retrieve activities: {str(e)}")
        return []

def get_activity_stats(workspace_id, days=7):
    """
    Get activity statistics for the workspace
    
    Args:
        workspace_id (int): Workspace ID
        days (int): Number of days to look back
    
    Returns:
        dict: Activity statistics
    """
    try:
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get total activities in the period
        total_activities = ActivityLog.query.filter(
            ActivityLog.workspace_id == workspace_id,
            ActivityLog.created_at >= cutoff_date
        ).count()
        
        # Get activities by type
        activity_counts = db.session.query(
            ActivityLog.action_type,
            db.func.count(ActivityLog.id).label('count')
        ).filter(
            ActivityLog.workspace_id == workspace_id,
            ActivityLog.created_at >= cutoff_date
        ).group_by(ActivityLog.action_type).all()
        
        # Get most active users
        user_activities = db.session.query(
            ActivityLog.user_email,
            db.func.count(ActivityLog.id).label('count')
        ).filter(
            ActivityLog.workspace_id == workspace_id,
            ActivityLog.created_at >= cutoff_date
        ).group_by(ActivityLog.user_email).order_by(
            db.func.count(ActivityLog.id).desc()
        ).limit(5).all()
        
        return {
            'total_activities': total_activities,
            'activity_counts': {item[0]: item[1] for item in activity_counts},
            'most_active_users': [{'email': item[0], 'count': item[1]} for item in user_activities]
        }
    except Exception as e:
        logging.error(f"Failed to get activity stats: {str(e)}")
        return {
            'total_activities': 0,
            'activity_counts': {},
            'most_active_users': []
        }

# Predefined log messages for common actions
class LogMessages:
    # Worker actions
    WORKER_CREATED = "Created worker: {name}"
    WORKER_UPDATED = "Updated worker: {name}"
    WORKER_DELETED = "Deleted worker: {name}"
    WORKERS_IMPORTED = "Imported {count} workers from file: {filename}"
    
    # Task actions
    TASK_CREATED = "Created task: {name}"
    TASK_UPDATED = "Updated task: {name}"
    TASK_DELETED = "Deleted task: {name}"
    TASK_COMPLETED = "Marked task as completed: {name}"
    
    # Company actions
    COMPANY_CREATED = "Created company: {name}"
    COMPANY_UPDATED = "Updated company information"
    COMPANY_CONTACT_UPDATED = "Updated company contact information"
    COMPANY_PAYOUT_UPDATED = "Updated daily payout rate to {currency}{amount}"
    
    # Team member actions
    TEAM_MEMBER_ADDED = "Added team member: {email} with role {role}"
    TEAM_MEMBER_ROLE_UPDATED = "Updated {email}'s role to {role}"
    TEAM_MEMBER_REMOVED = "Removed team member: {email}"
    
    # Attendance actions
    ATTENDANCE_RECORDED = "Recorded attendance for {worker_name} on {date}"
    ATTENDANCE_UPDATED = "Updated attendance for {worker_name} on {date}"
    
    # Report actions
    REPORT_GENERATED = "Generated {report_type} report"
    REPORT_EXPORTED = "Exported {report_type} report"
    
    # System actions
    USER_LOGIN = "Logged into workspace"
    USER_LOGOUT = "Logged out of workspace"
    WORKSPACE_JOINED = "Joined workspace"
    WORKSPACE_CREATED = "Created new workspace: {name}"
    
    # Import field actions
    IMPORT_FIELD_CREATED = "Created import field: {name}"
    IMPORT_FIELD_DELETED = "Deleted import field: {name}"
    
    # Report field actions
    REPORT_FIELD_CREATED = "Created report field: {name}"
    REPORT_FIELD_UPDATED = "Updated report field: {name}"
    REPORT_FIELD_DELETED = "Deleted report field: {name}"
