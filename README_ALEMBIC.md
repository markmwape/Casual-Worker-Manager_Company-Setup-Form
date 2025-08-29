# Alembic Database Migration System

This document explains how to use Alembic for database migrations in the Casual Worker Manager application.

## Overview

Your application has been successfully migrated from a manual SQL migration system to Alembic, which provides:

- **Version Control**: All database schema changes are tracked with unique revision IDs
- **Automatic Detection**: Schema changes are automatically detected from your SQLAlchemy models
- **Rollback Support**: You can easily rollback to previous database states
- **Environment Support**: Works with both local SQLite and Cloud SQL PostgreSQL

## Quick Start

### 1. Check Current Status
```bash
python3 -m alembic current
```

### 2. View Migration History
```bash
python3 -m alembic history --verbose
```

### 3. Apply All Pending Migrations
```bash
python3 run_alembic_migrations.py
```

### 4. Create a New Migration
```bash
python3 run_alembic_migrations.py create "Add new field to user table"
```

## File Structure

```
├── alembic/                    # Alembic configuration and migrations
│   ├── env.py                  # Alembic environment configuration
│   ├── script.py.mako          # Migration file template
│   └── versions/               # Migration files
│       └── d532020ac9ff_initial_migration_capture_current_schema.py
├── alembic.ini                 # Alembic configuration file
├── run_alembic_migrations.py   # Migration runner script
├── migrate_to_alembic.py       # Migration helper (one-time use)
├── MIGRATION_GUIDE.md          # Detailed migration guide
└── migrations_backup/          # Backup of old SQL migrations
```

## Environment Configuration

### Local Development (SQLite)
The application automatically uses SQLite for local development:
```bash
# No environment variables needed
python3 run_alembic_migrations.py
```

### Production (Cloud SQL)
Set these environment variables for Cloud SQL:

```bash
export DB_USER="your_db_user"
export DB_PASS="your_db_password"
export DB_NAME="your_db_name"
export DB_HOST="your_db_host"  # For direct connection
export CLOUD_SQL_CONNECTION_NAME="project:region:instance"  # For App Engine
```

## Making Schema Changes

### Step 1: Update Your Models
Edit your models in `models.py`:

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    # Add your new field here
    new_field = db.Column(db.String(100), nullable=True)
```

### Step 2: Generate Migration
```bash
python3 run_alembic_migrations.py create "Add new_field to user table"
```

This creates a new migration file in `alembic/versions/` with a name like:
`abc123def456_add_new_field_to_user_table.py`

### Step 3: Review the Migration
Always review the generated migration file before applying it:

```python
# alembic/versions/abc123def456_add_new_field_to_user_table.py
def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('user', sa.Column('new_field', sa.String(length=100), nullable=True))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user', 'new_field')
```

### Step 4: Apply the Migration
```bash
python3 run_alembic_migrations.py
```

## Useful Commands

### Check Migration Status
```bash
python3 -m alembic current
```

### View Migration History
```bash
python3 -m alembic history --verbose
```

### Apply All Pending Migrations
```bash
python3 -m alembic upgrade head
```

### Downgrade to Previous Version
```bash
python3 -m alembic downgrade -1
```

### Downgrade to Specific Version
```bash
python3 -m alembic downgrade d532020ac9ff
```

### Show Migration SQL (without applying)
```bash
python3 -m alembic upgrade head --sql
```

## Deployment

### Local Development
```bash
# Run migrations
python3 run_alembic_migrations.py

# Start the application
python3 main.py
```

### Production Deployment
The deployment script (`deploy.sh`) automatically runs migrations during deployment via the health check endpoint.

For manual deployment:
```bash
# Deploy to Cloud Run
./deploy.sh

# Or manually run migrations
python3 run_alembic_migrations.py
```

## Troubleshooting

### Migration Conflicts
If you encounter conflicts between your models and the database:

1. **Check current state**:
   ```bash
   python3 -m alembic current
   ```

2. **Reset to a known good state**:
   ```bash
   python3 -m alembic stamp head
   ```

3. **Generate a new migration**:
   ```bash
   python3 run_alembic_migrations.py create "Fix schema conflicts"
   ```

### Database Connection Issues

1. **Check environment variables**:
   ```bash
   python3 -c "from app_init import app; print(app.config['SQLALCHEMY_DATABASE_URI'])"
   ```

2. **Test connection**:
   ```bash
   python3 run_alembic_migrations.py
   ```

### Rollback to Old System
If you need to rollback to the old manual migration system:

1. Restore your database from backup
2. Copy SQL files from `migrations_backup/` back to `migrations/`
3. Use the old `run_migrations.py` script

## Best Practices

### 1. Always Review Migrations
Before applying any migration, review the generated file to ensure it does what you expect.

### 2. Test Migrations
Always test migrations on a copy of your production data before applying to production.

### 3. Backup Before Migrations
```bash
# For SQLite
cp database.sqlite database.sqlite.backup

# For PostgreSQL
pg_dump your_database > backup.sql
```

### 4. Use Descriptive Migration Messages
```bash
# Good
python3 run_alembic_migrations.py create "Add user profile picture field"

# Bad
python3 run_alembic_migrations.py create "Update"
```

### 5. Never Use `db.create_all()` in Production
Always use migrations for schema changes in production. The `db.create_all()` method should only be used for development and testing.

## Migration Examples

### Adding a New Table
```python
# In models.py
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

```bash
python3 run_alembic_migrations.py create "Add notification table"
```

### Adding a Column
```python
# In models.py - add to existing model
class User(db.Model):
    # ... existing fields ...
    phone_number = db.Column(db.String(20), nullable=True)
```

```bash
python3 run_alembic_migrations.py create "Add phone_number to user table"
```

### Modifying a Column
```python
# In models.py - change the field definition
class User(db.Model):
    # ... existing fields ...
    email = db.Column(db.String(200), unique=True, nullable=False)  # Increased length
```

```bash
python3 run_alembic_migrations.py create "Increase email field length"
```

## Environment-Specific Notes

### SQLite (Development)
- Migrations are applied immediately
- No special configuration needed
- Good for development and testing

### PostgreSQL (Production)
- Supports more complex schema changes
- Better performance for large datasets
- Requires proper connection configuration

## Support

If you encounter issues:

1. Check the migration history: `python3 -m alembic history`
2. Review the logs: `python3 run_alembic_migrations.py`
3. Check the database connection: `python3 -c "from app_init import app; print(app.config['SQLALCHEMY_DATABASE_URI'])"`
4. Review the migration files in `alembic/versions/`

## Migration from Old System

Your old SQL migration files have been backed up to `migrations_backup/`. The new Alembic system captures your current schema in the initial migration (`d532020ac9ff_initial_migration_capture_current_schema.py`).

You can safely remove the old migration files once you're confident the new system is working correctly. 