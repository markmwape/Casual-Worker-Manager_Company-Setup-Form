# Migration Guide

## Transitioning from Manual SQL Migrations to Alembic

Your application has been successfully migrated to use Alembic for database migrations. Here's how to work with migrations going forward:

### Current Status
- ✅ Alembic is configured and working
- ✅ Your current database schema is captured in the initial migration
- ✅ Old SQL migrations are backed up in `migrations_backup/`

### Making Schema Changes

1. **Update your models** in `models.py`
2. **Generate a migration**:
   ```bash
   python3 -m alembic revision --autogenerate -m "Description of changes"
   ```
3. **Review the generated migration** in `alembic/versions/`
4. **Apply the migration**:
   ```bash
   python3 -m alembic upgrade head
   ```

### Useful Commands

- Check current migration status: `python3 -m alembic current`
- View migration history: `python3 -m alembic history`
- Downgrade to previous version: `python3 -m alembic downgrade -1`
- Upgrade to latest: `python3 -m alembic upgrade head`

### Environment Variables

Make sure these environment variables are set for Cloud SQL:
- `DB_USER`: Database username
- `DB_PASS`: Database password  
- `DB_NAME`: Database name
- `DB_HOST`: Database host (for direct connection)
- `CLOUD_SQL_CONNECTION_NAME`: Cloud SQL connection name (for App Engine)

### Important Notes

- **Never use `db.create_all()` in production** - always use migrations
- **Always test migrations** on a copy of your production data
- **Backup your database** before running migrations in production
- **Review auto-generated migrations** before applying them

### Rollback Plan

If you need to rollback to the old system:
1. Restore your database from backup
2. Copy SQL files from `migrations_backup/` back to `migrations/`
3. Use the old `run_migrations.py` script

### Next Steps

1. Test the migration system in development
2. Update your deployment scripts to use Alembic
3. Consider removing the old migration files once you're confident
