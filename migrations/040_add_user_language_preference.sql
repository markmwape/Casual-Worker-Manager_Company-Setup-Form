"""Add language preference to User table"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_user_language_pref'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add language_preference column to user table
    try:
        op.add_column('user', sa.Column('language_preference', sa.String(10), nullable=True, server_default='en'))
    except Exception as e:
        print(f"Column might already exist: {e}")


def downgrade():
    try:
        op.drop_column('user', 'language_preference')
    except Exception as e:
        print(f"Could not drop column: {e}")
