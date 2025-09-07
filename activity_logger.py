import json
from datetime import datetime
from flask import session, request
from models import ActivityLog, db
import logging

def log_activity(action, description, user_email=None):
    """
    Simple activity logging
    
    Args:
        action (str): Action performed (e.g., 'Create Task', 'Update Worker', 'Login')
        description (str): Description of the action
        user_email (str, optional): User email (if not in session)
    """
    try:
        # Get user email from session if not provided
        if not user_email and 'user' in session and 'user_email' in session['user']:
            user_email = session['user']['user_email']
        
        # Get IP address and User Agent
        ip_address = request.remote_addr if request else None
        user_agent = request.headers.get('User-Agent') if request else None
        
        # Create activity log entry
        activity_log = ActivityLog(
            user_email=user_email,
            action=action,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(activity_log)
        db.session.commit()
        
        logging.info(f"Activity logged: {action} by {user_email}")
        
    except Exception as e:
        logging.error(f"Failed to log activity: {e}")
        # Don't let logging errors break the main functionality
        try:
            db.session.rollback()
        except:
            pass

def get_recent_activities(limit=50):
    """
    Get recent activities
    
    Args:
        limit (int): Maximum number of activities to return
    
    Returns:
        list: List of activity dictionaries
    """
    try:
        activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(limit).all()
        return [activity.to_dict() for activity in activities]
    except Exception as e:
        logging.error(f"Failed to get recent activities: {e}")
        return []

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
