import json
from datetime import datetime
from flask import session, request
from models import ActivityLog, db
import logging

def log_activity(action=None, description=None, user_email=None, action_type=None, resource_type=None, resource_id=None, details=None, workspace_id=None):
    """
    Unified activity logging function that handles both old and new API calls
    
    Old API:
        log_activity(action, description, user_email=None)
    
    New API:
        log_activity(action_type=str, resource_type=str, description=str, 
                    resource_id=int, details=dict, user_email=str, workspace_id=int)
    """
    try:
        # Handle new API format
        if action_type is not None:
            # Use action_type as provided
            final_action_type = action_type
            final_resource_type = resource_type
            final_resource_id = resource_id
            final_description = description
            
            # Add details to description if provided
            if details and isinstance(details, dict):
                # Add key details to description for better readability
                if 'task_name' in details:
                    final_description = f"{action_type.title()} task: {details['task_name']}"
                elif 'worker_name' in details:
                    final_description = f"{action_type.title()} worker: {details['worker_name']}"
                elif 'workspace_name' in details:
                    final_description = f"{action_type.title()} workspace: {details['workspace_name']}"
        
        # Handle old API format (backward compatibility)
        elif action is not None and description is not None:
            # Convert old format to new format
            final_action_type = action
            final_resource_type = 'system'
            final_resource_id = None
            final_description = description
            details = None
        else:
            logging.error("Invalid log_activity call - missing required parameters")
            return
        
        # Get user email from session if not provided
        if not user_email and 'user' in session and 'user_email' in session['user']:
            user_email = session['user']['user_email']
        
        # Get workspace_id from session if not provided
        if not workspace_id and 'current_workspace' in session:
            workspace_id = session['current_workspace'].get('id')
        
        # Get user_id from database if we have email
        user_id = None
        if user_email:
            try:
                from models import User
                user = User.query.filter_by(email=user_email).first()
                if user:
                    user_id = user.id
            except Exception as user_error:
                logging.warning(f"Could not get user_id for {user_email}: {user_error}")
        
        # Get IP address and User Agent
        ip_address = request.remote_addr if request else None
        user_agent = request.headers.get('User-Agent') if request else None
        
        # Convert details to JSON string if it's a dict
        details_json = None
        if details and isinstance(details, dict):
            try:
                details_json = json.dumps(details)
            except Exception as json_error:
                logging.warning(f"Could not serialize details to JSON: {json_error}")
        
        # Create activity log entry
        activity_log = ActivityLog(
            workspace_id=workspace_id,
            user_id=user_id,
            user_email=user_email,
            action_type=final_action_type,
            resource_type=final_resource_type,
            resource_id=final_resource_id,
            description=final_description,
            details=details_json,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(activity_log)
        db.session.commit()
        
        logging.info(f"Activity logged: {final_action_type} {final_resource_type} by {user_email}")
        
    except Exception as e:
        logging.error(f"Failed to log activity: {e}")
        import traceback
        logging.error(f"Activity logging traceback: {traceback.format_exc()}")
        # Don't let logging errors break the main functionality
        try:
            db.session.rollback()
        except:
            pass

def get_recent_activities(workspace_id=None, limit=50):
    """
    Get recent activities, optionally filtered by workspace
    
    Args:
        workspace_id (int, optional): Workspace ID to filter by
        limit (int): Maximum number of activities to return
    
    Returns:
        list: List of activity dictionaries
    """
    try:
        query = ActivityLog.query
        
        if workspace_id:
            query = query.filter(ActivityLog.workspace_id == workspace_id)
        
        activities = query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
        return [activity.to_dict() for activity in activities]
    except Exception as e:
        logging.error(f"Failed to get recent activities: {e}")
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
