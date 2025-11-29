"""Add enable_duplicate_detection column to import_field table

Revision ID: 051
Revises: 2c65fbb8ec7f
Create Date: 2025-11-29 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '051'
down_revision = '2c65fbb8ec7f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply the migration - add enable_duplicate_detection column"""
    try:
        # Add the column if it doesn't exist
        op.add_column('import_field', 
                     sa.Column('enable_duplicate_detection', sa.Boolean(), 
                              nullable=False, server_default=sa.false()))
        print("✅ Added enable_duplicate_detection column to import_field")
    except Exception as e:
        print(f"Column may already exist: {e}")
        pass
    
    # Create index for efficient queries
    try:
        op.create_index('idx_import_field_duplicate_detection',
                       'import_field',
                       ['company_id', 'enable_duplicate_detection'],
                       if_not_exists=True)
        print("✅ Created index idx_import_field_duplicate_detection")
    except Exception as e:
        print(f"Index may already exist: {e}")
        pass


def downgrade() -> None:
    """Revert the migration - remove the column"""
    try:
        op.drop_index('idx_import_field_duplicate_detection', 
                     table_name='import_field')
        print("✅ Dropped index idx_import_field_duplicate_detection")
    except Exception as e:
        print(f"Index doesn't exist or couldn't be dropped: {e}")
        pass
    
    try:
        op.drop_column('import_field', 'enable_duplicate_detection')
        print("✅ Removed enable_duplicate_detection column from import_field")
    except Exception as e:
        print(f"Column doesn't exist or couldn't be dropped: {e}")
        pass
