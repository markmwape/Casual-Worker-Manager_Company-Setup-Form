# Embee Accounting - Casual Worker Manager

A comprehensive workforce management platform for managing casual workers, attendance tracking, task assignment, and payroll calculations.

## Features

### Core Features
- **Workspace Management**: Multi-tenant workspaces with role-based access control
- **Worker Management**: Add, manage, and track casual workers with custom fields
- **Task Management**: Create and assign tasks with flexible payment structures
- **Attendance Tracking**: Real-time attendance monitoring with status tracking
- **Reporting**: Advanced reporting with custom fields and formula calculations
- **Team Collaboration**: Multi-user workspaces with different permission levels

### Authentication & Security
- Firebase Authentication integration
- Session management with secure cookies
- Email-based sign-in with workspace selection
- Role-based access control (Admin, Accountant, Supervisor)

### Subscription Management
- Multiple subscription tiers (Trial, Starter, Growth, Enterprise, Corporate)
- Stripe integration for payments
- Automatic trial management
- Feature-based access control

### UI/UX Features
- Modern, responsive design with Tailwind CSS and DaisyUI
- Dark/light theme support
- Mobile-friendly interface
- Real-time form validation
- Progress indicators and loading states
- Success animations and feedback

## Tech Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: Database ORM
- **SQLite/PostgreSQL**: Database (SQLite for development, PostgreSQL for production)
- **Alembic**: Database migrations
- **Stripe**: Payment processing
- **Firebase Admin SDK**: Authentication

### Frontend
- **HTML5/CSS3**: Modern web standards
- **Tailwind CSS**: Utility-first CSS framework
- **DaisyUI**: Component library for Tailwind CSS
- **JavaScript ES6+**: Modern JavaScript
- **Firebase SDK**: Client-side authentication

### Infrastructure
- **Google Cloud Run**: Container deployment
- **Google Cloud SQL**: Managed PostgreSQL
- **Gunicorn**: WSGI server
- **Docker**: Containerization

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+ (for frontend dependencies)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/casual-worker-manager.git
   cd casual-worker-manager
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   # Flask Configuration
   FLASK_APP=main.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   
   # Database Configuration
   # For local development (SQLite)
   SQLALCHEMY_DATABASE_URI=sqlite:///database.sqlite
   
   # For production (PostgreSQL)
   # DB_HOST=your-postgres-host
   # DB_USER=your-postgres-user
   # DB_PASS=your-postgres-password
   # DB_NAME=your-database-name
   # INSTANCE_CONNECTION_NAME=your-cloud-sql-instance
   
   # Stripe Configuration
   STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
   
   # Firebase Configuration
   # Add your Firebase service account JSON content as environment variables
   # or use the Firebase Admin SDK with a service account file
   
   # Master Admin
   MASTER_ADMIN_EMAIL=admin@yourcompany.com
   ```

5. **Initialize the database**
   ```bash
   flask db upgrade  # If using Alembic migrations
   # OR
   python -c "from app_init import app, db; db.create_all()"
   ```

6. **Run the development server**
   ```bash
   python main.py
   # OR
   flask run --debug --host=0.0.0.0 --port=5000
   ```

7. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

### Production Deployment

#### Google Cloud Run Deployment

1. **Build and deploy**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/casual-worker-manager
   gcloud run deploy --image gcr.io/PROJECT_ID/casual-worker-manager --platform managed
   ```

2. **Set environment variables**
   ```bash
   gcloud run services update casual-worker-manager \
     --set-env-vars INSTANCE_CONNECTION_NAME=PROJECT_ID:REGION:INSTANCE_NAME \
     --set-env-vars DB_USER=postgres \
     --set-env-vars DB_PASS=your_password \
     --set-env-vars DB_NAME=casual_worker_db
   ```

#### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t casual-worker-manager .
   ```

2. **Run the container**
   ```bash
   docker run -p 8080:8080 \
     -e INSTANCE_CONNECTION_NAME=your-connection-name \
     -e DB_USER=postgres \
     -e DB_PASS=your-password \
     -e DB_NAME=casual_worker_db \
     casual-worker-manager
   ```

## Configuration

### Database Configuration

#### SQLite (Development)
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///database.sqlite'
```

#### PostgreSQL (Production)
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@host:port/database'
```

#### Google Cloud SQL
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@/database?host=/cloudsql/connection-name'
```

### Stripe Configuration

1. **Create a Stripe account** at [stripe.com](https://stripe.com)
2. **Get your API keys** from the Stripe Dashboard
3. **Set up webhooks** pointing to `https://your-domain.com/stripe/webhook`
4. **Configure products and prices** in the Stripe Dashboard for subscription tiers

### Firebase Configuration

1. **Create a Firebase project** at [console.firebase.google.com](https://console.firebase.google.com)
2. **Enable Authentication** with Email/Password and Email Link providers
3. **Download service account key** and set environment variables
4. **Configure authorized domains** for your deployment

## API Documentation

### Authentication Endpoints

#### POST `/set_session`
Set user session after Firebase authentication
```json
{
  "email": "user@example.com",
  "displayName": "User Name",
  "photoURL": "https://...",
  "uid": "firebase-uid",
  "workspace_data": { ... }
}
```

### Workspace Endpoints

#### POST `/api/workspace/create`
Create a new workspace
```json
{
  "company_name": "Company Name",
  "country": "Country",
  "industry_type": "Industry",
  "company_phone": "+1234567890",
  "company_email": "company@example.com",
  "expected_workers": "below_100"
}
```

#### POST `/api/workspace/join`
Join an existing workspace
```json
{
  "workspace_code": "16-CHAR-CODE"
}
```

#### POST `/api/user/workspaces`
Get user's workspaces
```json
{
  "email": "user@example.com"
}
```

### Worker Management Endpoints

#### POST `/api/worker`
Create a new worker
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-01",
  "custom_field_name": "custom_value"
}
```

#### GET `/workers`
View workers page (HTML)

### Task Management Endpoints

#### POST `/api/task`
Create a new task
```json
{
  "name": "Task Name",
  "description": "Task Description",
  "start_date": "2024-01-01T00:00:00",
  "payment_type": "per_day",
  "per_day_payout": 50.00,
  "per_day_currency": "USD"
}
```

#### GET `/tasks`
View tasks page (HTML)

### Subscription Endpoints

#### POST `/stripe/webhook`
Handle Stripe webhooks for subscription updates

#### GET `/api/workspace/payments`
Get workspace subscription information

## Database Schema

### Core Tables

#### Users
- `id`: Primary key
- `email`: User email (unique)
- `profile_picture`: Profile picture URL
- `created_at`: Account creation timestamp

#### Workspaces
- `id`: Primary key
- `name`: Workspace name
- `workspace_code`: 16-character unique code
- `country`: Country location
- `industry_type`: Industry classification
- `subscription_status`: Current subscription status
- `subscription_tier`: Current subscription tier
- `trial_end_date`: Trial expiration date
- `created_by`: Creator user ID

#### Companies
- `id`: Primary key
- `name`: Company name
- `workspace_id`: Associated workspace
- `phone`: Company phone number
- `daily_payout_rate`: Default daily payout rate
- `currency`: Currency code

#### Workers
- `id`: Primary key
- `first_name`: Worker first name
- `last_name`: Worker last name
- `date_of_birth`: Worker birth date
- `company_id`: Associated company

#### Tasks
- `id`: Primary key
- `name`: Task name
- `description`: Task description
- `start_date`: Task start date
- `status`: Task status (Pending, In Progress, Completed)
- `payment_type`: Payment structure (per_day, per_part)
- `company_id`: Associated company

#### Attendance
- `id`: Primary key
- `worker_id`: Associated worker
- `task_id`: Associated task
- `date`: Attendance date
- `status`: Attendance status (Present, Absent)
- `check_in_time`: Check-in timestamp
- `check_out_time`: Check-out timestamp

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add some feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

### Development Guidelines

- Follow PEP 8 for Python code style
- Write tests for new features
- Update documentation for API changes
- Use meaningful commit messages
- Ensure all tests pass before submitting PR

### Testing

```bash
# Run Python tests
python -m pytest tests/

# Run linting
flake8 .

# Run type checking
mypy .
```

## Security

### Authentication
- Firebase Authentication with email verification
- Secure session management
- JWT token validation

### Authorization
- Role-based access control
- Workspace-level permissions
- API endpoint protection

### Data Protection
- HTTPS encryption in production
- Secure cookie configuration
- SQL injection prevention with SQLAlchemy
- XSS protection with template escaping

### Privacy
- GDPR compliance considerations
- Data retention policies
- User data deletion capabilities

## Support

### Documentation
- API documentation available at `/api/docs` (when enabled)
- User guides in the `/docs` directory
- FAQ and troubleshooting guides

### Community
- GitHub Issues for bug reports and feature requests
- Discord server for community support
- Stack Overflow tag: `embee-accounting`

### Professional Support
- Email: support@embeeaccounting.com
- Business hours: Monday-Friday, 9 AM - 5 PM UTC
- Response time: Within 24 hours for paid plans

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Changelog

### Version 2.0.0 (Current)
- Added subscription management with Stripe integration
- Improved UI/UX with modern design
- Enhanced error handling and validation
- Added comprehensive API documentation
- Implemented role-based access control
- Added multi-workspace support

### Version 1.0.0
- Initial release with basic worker and task management
- Firebase authentication integration
- Basic attendance tracking
- Simple reporting features

## Roadmap

### Q1 2024
- [ ] Mobile app development (React Native)
- [ ] Advanced analytics dashboard
- [ ] Automated payroll calculations
- [ ] Integration with accounting software

### Q2 2024
- [ ] Time tracking with GPS verification
- [ ] Document management system
- [ ] Performance analytics
- [ ] Multi-language support

### Q3 2024
- [ ] API rate limiting
- [ ] Advanced reporting with charts
- [ ] Bulk import/export features
- [ ] Automated notifications

### Q4 2024
- [ ] Machine learning for workforce optimization
- [ ] Advanced security features
- [ ] Enterprise SSO integration
- [ ] Custom branding options
