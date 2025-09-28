#!/bin/bash

# Create new GitHub repository and clean deployment
set -e

REPO_NAME="Casual-Worker-Manager_Company-Setup-Form"
GITHUB_USERNAME="markmwape"

echo "🆕 Creating new GitHub repository: $REPO_NAME"

# Create the repository on GitHub using gh CLI
gh repo create $REPO_NAME --public --description "Casual Worker Manager Company Setup Form - Clean Deployment"

echo "📁 Setting up clean local repository..."

# Create a temporary directory for the clean repo
TEMP_DIR="../${REPO_NAME}_clean"
mkdir -p $TEMP_DIR
cd $TEMP_DIR

# Initialize new git repository
git init
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

echo "📋 Copying essential files..."

# Copy only the necessary files (excluding .git, node_modules, etc.)
cp -r "../Casual Worker Manager_Company Setup Form"/*.py .
cp -r "../Casual Worker Manager_Company Setup Form"/*.txt .
cp -r "../Casual Worker Manager_Company Setup Form"/*.md .
cp -r "../Casual Worker Manager_Company Setup Form"/*.ini .
cp -r "../Casual Worker Manager_Company Setup Form"/*.log . 2>/dev/null || true
cp -r "../Casual Worker Manager_Company Setup Form"/*.sh .
cp -r "../Casual Worker Manager_Company Setup Form"/*.yaml .
cp -r "../Casual Worker Manager_Company Setup Form"/Dockerfile .
cp -r "../Casual Worker Manager_Company Setup Form"/templates .
cp -r "../Casual Worker Manager_Company Setup Form"/static .
cp -r "../Casual Worker Manager_Company Setup Form"/migrations .
cp -r "../Casual Worker Manager_Company Setup Form"/alembic .
cp -r "../Casual Worker Manager_Company Setup Form"/uploads . 2>/dev/null || true

echo "🚫 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Environment variables
.env
.env.local

# Firebase
.firebase/
firebase-debug.log
.firebaserc

# Google Cloud
.gcloudignore

# Uploads
uploads/
temp/

# Node modules (if any)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
EOF

echo "📝 Creating README.md..."
cat > README.md << 'EOF'
# Casual Worker Manager Company Setup Form

A Flask web application for managing casual workers and company setup forms.

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
EOF

echo "🔧 Making scripts executable..."
chmod +x *.sh

echo "📤 Committing and pushing to GitHub..."
git add .
git commit -m "Initial commit: Clean deployment setup"
git branch -M main
git push -u origin main

echo "✅ Successfully created new repository!"
echo "📍 Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "🔗 You can now deploy from this clean repository to Google Cloud Run"

# Return to original directory
cd "../Casual Worker Manager_Company Setup Form"

echo ""
echo "🚀 Next steps:"
echo "1. Go to Google Cloud Console: https://console.cloud.google.com/run?project=embee-accounting"
echo "2. Click 'Deploy' -> 'From repository'"
echo "3. Connect the new repository: $GITHUB_USERNAME/$REPO_NAME"
echo "4. Set memory to 4Gi in the deployment configuration"
echo "5. Add the environment variables for Cloud SQL"
