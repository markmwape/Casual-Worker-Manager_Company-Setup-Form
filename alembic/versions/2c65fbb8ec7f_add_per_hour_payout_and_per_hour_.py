"""Add per_hour_payout and per_hour_currency to Task model and hours_worked to Attendance model

Revision ID: 2c65fbb8ec7f
Revises: 0abd8efc6565
Create Date: 2025-11-13 09:53:50.302860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c65fbb8ec7f'
down_revision: Union[str, Sequence[str], None] = '0abd8efc6565'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add per_hour fields to task table
    op.add_column('task', sa.Column('per_hour_payout', sa.Float(), nullable=True))
    op.add_column('task', sa.Column('per_hour_currency', sa.String(length=10), nullable=True))
    
    # Add hours_worked field to attendance table
    op.add_column('attendance', sa.Column('hours_worked', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove hours_worked field from attendance table
    op.drop_column('attendance', 'hours_worked')
    
    # Remove per_hour fields from task table
    op.drop_column('task', 'per_hour_currency')
    op.drop_column('task', 'per_hour_payout')
