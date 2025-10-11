from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import Flask app and models
from app_init import app
from models import db

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from environment variables
def get_database_url():
    """Get database URL from environment variables"""
    # Allow explicit DATABASE_URL override
    if os.environ.get('DATABASE_URL'):
        return os.environ.get('DATABASE_URL')
    # Production via Cloud Run when DB_HOST or Cloud SQL connection is configured
    if os.environ.get('DB_HOST') or os.environ.get('CLOUD_SQL_CONNECTION_NAME') or os.environ.get('INSTANCE_CONNECTION_NAME'):
         # Production: Use Cloud SQL
         db_user = os.environ.get('DB_USER', 'cwuser')
         db_pass = os.environ.get('DB_PASS', '')
         db_name = os.environ.get('DB_NAME', 'cw_manager')
         
         # For Cloud SQL Proxy
         # Prefer INSTANCE_CONNECTION_NAME for Cloud Run compatibility
         connection_name = os.environ.get('INSTANCE_CONNECTION_NAME') or os.environ.get('CLOUD_SQL_CONNECTION_NAME')
         if connection_name:
             # Use the Cloud SQL connection format
             return f'postgresql://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{connection_name}'
         else:
            db_host = os.environ.get('DB_HOST')
            return f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}'
    else:
        # Development: Use SQLite
        return 'sqlite:///database.sqlite'

# Set the database URL in the config
config.set_main_option("sqlalchemy.url", get_database_url())

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
