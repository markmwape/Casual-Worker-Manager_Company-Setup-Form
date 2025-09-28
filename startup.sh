#!/bin/bash
set -e

echo "Starting Casual Worker Manager..."

# Try emergency migration first
echo "Running emergency migration to add missing columns..."
if python3 emergency_migration.py 2>&1; then
    echo "Emergency migration completed successfully"
else
    echo "Emergency migration failed, trying Alembic..."
    # Try to run migrations, but don't fail if they don't work
    echo "Attempting to run Alembic migrations..."
    if python3 -m alembic upgrade head 2>&1; then
        echo "Alembic migrations completed successfully"
    else
        echo "Alembic migrations failed, continuing anyway..."
    fi
fi

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn wsgi:app -b 0.0.0.0:8080 --workers 1 --timeout 300 --log-level info --access-logfile - --error-logfile -
