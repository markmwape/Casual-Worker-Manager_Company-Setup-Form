from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets
import string

db = SQLAlchemy()

# Association table for task-worker relationship
task_workers = db.Table('task_workers',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('worker_id', db.Integer, db.ForeignKey('worker.id'), primary_key=True)
)

class Workspace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    workspace_code = db.Column(db.String(16), unique=True, nullable=False)  # Changed from 'code' to 'workspace_code'
    address = db.Column(db.Text, nullable=True)  # Made nullable for backward compatibility
    country = db.Column(db.String(100), nullable=False)
    industry_type = db.Column(db.String(100), nullable=False)
    company_phone = db.Column(db.String(20), nullable=False)
    company_email = db.Column(db.String(150), nullable=False)
    expected_workers = db.Column(db.Integer, nullable=True)  # Keep for backward compatibility
    expected_workers_string = db.Column(db.String(50), nullable=False)  # New column for range format
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    subscription_status = db.Column(db.String(50), default='trial')
    subscription_tier = db.Column(db.String(50), default='trial')
    trial_end_date = db.Column(db.DateTime, nullable=True)
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    users = db.relationship('UserWorkspace', back_populates='workspace', cascade='all, delete-orphan')
    companies = db.relationship('Company', backref='workspace', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Workspace, self).__init__(**kwargs)
        if not self.workspace_code:
            self.workspace_code = self.generate_workspace_code()
        if not self.trial_end_date:
            from datetime import timedelta
            self.trial_end_date = datetime.utcnow() + timedelta(days=30)
    
    def generate_workspace_code(self):
        """Generate a unique 16-character workspace code"""
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))
            if not Workspace.query.filter_by(workspace_code=code).first():
                return code
    
    @property
    def code(self):
        """Property to maintain compatibility with existing code"""
        return self.workspace_code
    
    def to_dict(self):
        """Convert to dictionary for debugging"""
        return {
            'id': self.id,
            'name': self.name,
            'workspace_code': self.workspace_code,
            'country': self.country,
            'industry_type': self.industry_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'subscription_status': self.subscription_status
        }

class UserWorkspace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspace.id'), nullable=False)
    role = db.Column(db.String(20), default='Supervisor')  # Admin, Accountant, Supervisor
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'workspace_id', name='uq_user_workspace'),)
    # Relationships
    user = db.relationship('User', back_populates='workspaces')
    workspace = db.relationship('Workspace', back_populates='users')

class ReportField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(50), nullable=False)
    formula = db.Column(db.Text)
    max_limit = db.Column(db.Float, nullable=True)  # New field for maximum limit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payout_type = db.Column(db.String(20), nullable=False, default='per_day')

class ImportField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(50), nullable=True)
    enable_duplicate_detection = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    custom_field_values = db.relationship('WorkerCustomFieldValue', backref='import_field', lazy=True, cascade='all, delete-orphan')

class WorkerCustomFieldValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable=False)
    custom_field_id = db.Column(db.Integer, db.ForeignKey('import_field.id'), nullable=False)
    value = db.Column(db.String(255), nullable=True)

class WorkerImportLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    total_records = db.Column(db.Integer, nullable=False)
    successful_imports = db.Column(db.Integer, nullable=False)
    duplicate_records = db.Column(db.Integer, nullable=False)
    error_records = db.Column(db.Integer, nullable=False)
    error_details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    profile_picture = db.Column(db.String(255))
    role = db.Column(db.String(20), default='Viewer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    companies = db.relationship('Company', backref='creator', lazy=True)
    workers = db.relationship('Worker', backref='creator', lazy=True)
    workspaces = db.relationship('UserWorkspace', back_populates='user')
    
    def get_workspace_role(self, workspace_id):
        """Get user's role in a specific workspace"""
        user_workspace = UserWorkspace.query.filter_by(
            user_id=self.id, 
            workspace_id=workspace_id
        ).first()
        return user_workspace.role if user_workspace else None
    
    def is_admin_in_workspace(self, workspace_id):
        """Check if user is admin in a specific workspace"""
        return self.get_workspace_role(workspace_id) == 'Admin'
    
    def is_accountant_in_workspace(self, workspace_id):
        """Check if user is accountant in a specific workspace"""
        role = self.get_workspace_role(workspace_id)
        return role in ['Admin', 'Accountant']
    
    def is_supervisor_in_workspace(self, workspace_id):
        """Check if user is supervisor or higher in a specific workspace"""
        role = self.get_workspace_role(workspace_id)
        return role in ['Admin', 'Accountant', 'Supervisor']
    
    def to_dict(self):
        """Convert to dictionary for debugging"""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    registration_number = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspace.id'), nullable=False)
    workers = db.relationship('Worker', backref='company', lazy=True, cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='company', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='company', lazy=True, cascade='all, delete-orphan')
    import_fields = db.relationship('ImportField', backref='company', lazy=True, cascade='all, delete-orphan')
    report_fields = db.relationship('ReportField', backref='company', lazy=True, cascade='all, delete-orphan')
    worker_import_logs = db.relationship('WorkerImportLog', backref='company', lazy=True, cascade='all, delete-orphan')
    daily_payout_rate = db.Column(db.Float, default=56.0, nullable=False)
    currency = db.Column(db.String(3), default='ZMW', nullable=False)  # ISO 4217 currency code
    currency_symbol = db.Column(db.String(5), default='K', nullable=False)  # Currency symbol
    phone = db.Column(db.String(20), nullable=False)  # Add this line

class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    attendance_records = db.relationship('Attendance', backref='worker', lazy=True, cascade='all, delete-orphan')
    custom_field_values = db.relationship('WorkerCustomFieldValue', backref='worker', lazy=True, cascade='all, delete-orphan')
    tasks = db.relationship('Task', secondary=task_workers, backref=db.backref('workers', lazy='dynamic'))
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Pending')
    start_date = db.Column(db.DateTime, nullable=False)
    completion_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    # Added fields
    payment_type = db.Column(db.String(20), nullable=False, default='per_day')
    per_part_rate = db.Column(db.Float, nullable=True)
    per_part_payout = db.Column(db.Float, nullable=True)  # Alias for per_part_rate, for template compatibility
    per_part_currency = db.Column(db.String(10), nullable=True)
    # Per-day payment fields
    per_day_payout = db.Column(db.Float, nullable=True)  # Individual daily payout for this task
    per_day_currency = db.Column(db.String(10), nullable=True)  # Currency for daily payout
    # Per-hour payment fields
    per_hour_payout = db.Column(db.Float, nullable=True)  # Hourly rate for this task
    per_hour_currency = db.Column(db.String(10), nullable=True)  # Currency for hourly payout
    # Relationships
    attendance_records = db.relationship('Attendance', backref='task', lazy=True, cascade='all, delete-orphan')

class MasterAdmin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('master_admin.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        """Convert to dictionary for debugging"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(150), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_email': self.user_email,
            'action': self.action,
            'description': self.description,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=True)
    check_out_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default='Absent')
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    # Added fields
    units_completed = db.Column(db.Integer, nullable=True)
    hours_worked = db.Column(db.Float, nullable=True)  # Hours worked for per_hour tasks