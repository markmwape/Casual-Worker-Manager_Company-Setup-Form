#!/bin/bash
set -e

echo "Starting Casual Worker Manager..."

# Try to run migrations, but don't fail if they don't work
echo "Attempting to run Alembic migrations..."
if python3 -m alembic upgrade head 2>&1; then
    echo "Migrations completed successfully"
else
    echo "Migrations failed or not needed, continuing..."
fi

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn wsgi:app -b 0.0.0.0:8080 --workers 1 --timeout 300 --log-level info --access-logfile - --error-logfile -
