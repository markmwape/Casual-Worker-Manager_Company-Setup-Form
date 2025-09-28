"""Initial migration - capture current schema

Revision ID: d532020ac9ff
Revises: 
Create Date: 2025-08-02 11:16:00.211186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'd532020ac9ff'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Get the bind and inspector to guard table creation
    conn = op.get_bind()
    inspector = inspect(conn)

    # Create master_admin table only if it doesn't exist
    if not inspector.has_table('master_admin'):
        op.create_table('master_admin',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['master_admin.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
        )
    
    # Create user table only if it doesn't exist
    if not inspector.has_table('user'):
        op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('profile_picture', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
        )

    # Create workspace table only if it doesn't exist
    if not inspector.has_table('workspace'):
        op.create_table('workspace',
        sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('workspace_code', sa.String(length=16), nullable=False),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('country', sa.String(length=100), nullable=False),
    sa.Column('industry_type', sa.String(length=100), nullable=False),
    sa.Column('company_phone', sa.String(length=20), nullable=False),
    sa.Column('company_email', sa.String(length=150), nullable=False),
    sa.Column('expected_workers', sa.Integer(), nullable=True),
    sa.Column('expected_workers_string', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
    sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
    sa.Column('subscription_status', sa.String(length=50), nullable=True),
    sa.Column('trial_end_date', sa.DateTime(), nullable=True),
    sa.Column('subscription_end_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('workspace_code')
    )
    
    # Create company table only if it doesn't exist
    if not inspector.has_table('company'):
        op.create_table('company',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('registration_number', sa.String(length=100), nullable=False),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('industry', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=False),
        sa.Column('daily_payout_rate', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('currency_symbol', sa.String(length=5), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspace.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    
    # Create user_workspace table only if it doesn't exist
    if not inspector.has_table('user_workspace'):
        op.create_table('user_workspace',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspace.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    
    # Create import_field table only if it doesn't exist
    if not inspector.has_table('import_field'):
        op.create_table('import_field',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('field_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    
    # Create report_field table only if it doesn't exist
    if not inspector.has_table('report_field'):
        op.create_table('report_field',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('field_type', sa.String(length=50), nullable=False),
        sa.Column('formula', sa.Text(), nullable=True),
        sa.Column('max_limit', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('payout_type', sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    
    # Create task table only if it doesn't exist
    if not inspector.has_table('task'):
        op.create_table('task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('completion_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('payment_type', sa.String(length=20), nullable=False),
        sa.Column('per_part_rate', sa.Float(), nullable=True),
        sa.Column('per_part_payout', sa.Float(), nullable=True),
        sa.Column('per_part_currency', sa.String(length=10), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    
    # Create worker table only if it doesn't exist
    if not inspector.has_table('worker'):
        op.create_table('worker',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    
    # Create worker_import_log table only if it doesn't exist
    if not inspector.has_table('worker_import_log'):
        op.create_table('worker_import_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('total_records', sa.Integer(), nullable=False),
        sa.Column('successful_imports', sa.Integer(), nullable=False),
        sa.Column('duplicate_records', sa.Integer(), nullable=False),
        sa.Column('error_records', sa.Integer(), nullable=False),
        sa.Column('error_details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    
    # Create attendance table only if it doesn't exist
    if not inspector.has_table('attendance'):
        op.create_table('attendance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('worker_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('check_in_time', sa.DateTime(), nullable=True),
        sa.Column('check_out_time', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('units_completed', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
        sa.ForeignKeyConstraint(['worker_id'], ['worker.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    
    # Create task_workers table only if it doesn't exist
    if not inspector.has_table('task_workers'):
        op.create_table('task_workers',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('worker_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
        sa.ForeignKeyConstraint(['worker_id'], ['worker.id'], ),
        sa.PrimaryKeyConstraint('task_id', 'worker_id')
        )
    
    # Create worker_custom_field_value table only if it doesn't exist
    if not inspector.has_table('worker_custom_field_value'):
        op.create_table('worker_custom_field_value',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('worker_id', sa.Integer(), nullable=False),
        sa.Column('custom_field_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['custom_field_id'], ['import_field.id'], ),
        sa.ForeignKeyConstraint(['worker_id'], ['worker.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('worker_custom_field_value')
    op.drop_table('task_workers')
    op.drop_table('attendance')
    op.drop_table('worker_import_log')
    op.drop_table('worker')
    op.drop_table('task')
    op.drop_table('report_field')
    op.drop_table('import_field')
    op.drop_table('user_workspace')
    op.drop_table('company')
    op.drop_table('workspace')
    op.drop_table('user')
    op.drop_table('master_admin')
    # ### end Alembic commands ###
