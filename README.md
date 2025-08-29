# Casual Worker Manager Company Setup Form

A Flask web application for managing casual workers and company setup forms.

## Status
🚀 Ready for deployment to Google Cloud Run with 4Gi memory configuration.

## Features

- User authentication with Firebase
- Company registration and management
- Worker management system
- Task assignment and tracking
- Attendance management
- Reporting system

## Tech Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL (Cloud SQL)
- **Authentication**: Firebase Auth
- **Deployment**: Google Cloud Run
- **Database Migrations**: Alembic

## Environment Variables

- `CLOUD_SQL_CONNECTION_NAME`: Cloud SQL connection name
- `DB_USER`: Database username
- `DB_PASS`: Database password
- `DB_NAME`: Database name

## Deployment

Deploy to Google Cloud Run:

```bash
bash deploy.sh
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables

3. Run the application:
```bash
python main.py
```

## Database Migrations

Run migrations:
```bash
python run_alembic_migrations.py
```
