
# Multi-Tenant SaaS Authentication Backend

This is a backend API built with Python and Flask for handling authentication, authorization, and organization management in a multi-tenant SaaS environment. The system allows user sign-up, sign-in, organization creation, member role assignment, and invite management with email notifications.

## Features

### Authentication & Authorization
- **Sign Up**: Create users and organizations. The creator is assigned the owner role.
- **Sign In**: Authenticate users with JWT-based access and refresh tokens.
- **Password Reset**: Allows users to reset their password.
- **Role-Based Access Control (RBAC)**: Manage organization-specific roles for users.
- **Multi-Tenant Support**: Users can belong to multiple organizations with distinct roles.

### Organization and Member Management
- **Create Organization**: Users can create organizations.
- **Invite Members**: Send email invites to users to join an organization with a specific role.
- **Update Member Roles**: Update roles by using role names.
- **Delete Member**: Remove a user from an organization.

### Invitation System
- **Invite Members**: Generate an invite token sent via email.
- **Accept Invitation**: Users accept invites and join the organization.
- **Auto Expire Invitations**: Expire invitations after 10 minutes.

### Background Jobs
- **Scheduled Task**: A background task to automatically delete expired invites every minute.

### Email Notifications
- **Gmail SMTP**: Use Gmail's SMTP service to send email notifications.
- **Email Types**:
  - Invitation Emails
  - Password Reset Alerts
  - Login Event Alerts

### JWT Token Authentication
- **Access Token**: Authorize API requests.
- **Refresh Token**: Renew access tokens after expiration.

## Technology Stack

- **Flask**: Web framework for REST API development.
- **Flask-SQLAlchemy**: ORM for database operations.
- **MySQL**: Database for data storage.
- **Flask-JWT-Extended**: JWT-based authentication.
- **APScheduler**: Scheduler for background jobs.
- **PyMySQL**: MySQL connector for Python.
- **Flask-Migrate**: Database migration management.
- **Gmail SMTP**: For sending emails.

## Database Schema

### Tables

1. **Organization**
    - `id`: Unique identifier.
    - `name`: Organization name.
    - `status`: Organization status.
    - `personal`: Boolean flag for personal organizations.
    - `settings`: JSON for organization settings.
    - `created_at`: Creation timestamp.
    - `updated_at`: Update timestamp.

2. **User**
    - `id`: Unique identifier.
    - `email`: User's email.
    - `password`: Encrypted password.
    - `profile`: JSON for user profile.
    - `status`: User status.
    - `settings`: JSON for user settings.
    - `created_at`: Creation timestamp.
    - `updated_at`: Update timestamp.

3. **Role**
    - `id`: Unique identifier.
    - `name`: Role name (e.g., Owner, Admin, Member).
    - `description`: Role description.
    - `org_id`: Organization foreign key.

4. **Member**
    - `id`: Unique identifier.
    - `org_id`: Organization foreign key.
    - `user_id`: User foreign key.
    - `role_id`: Role foreign key.
    - `status`: Membership status.
    - `settings`: JSON for member settings.
    - `created_at`: Creation timestamp.
    - `updated_at`: Update timestamp.

5. **Invite**
    - `id`: Unique identifier.
    - `token`: Invitation token.
    - `user_id`: User foreign key.
    - `org_id`: Organization foreign key.
    - `created_at`: Creation timestamp.

6. **Version**
    - `id`: Unique identifier.
    - `version`: Application version.
    - `description`: Version description.
    - `created_at`: Creation timestamp.

## Project Structure

```
multi-tenant-saas-backend/
│
├── app.py                  # Main Flask application
├── models.py               # SQLAlchemy models
├── scheduler.py            # Background jobs (using APScheduler)
├── config.py               # App configuration
├── requirements.txt        # Python dependencies
├── .venv/                  # Python virtual environment
└── migrations/             # Flask-Migrate migration scripts
```

## Installation

1. **Clone the repository**:

```bash
git clone https://github.com/username/multi-tenant-saas-backend.git
cd multi-tenant-saas-backend
```

2. **Create and activate a virtual environment**:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

4. **Set up environment variables** in `.env` file:

```

SECRET_KEY=your-secret-key
EMAIL_USER="apitestingformultitenant@gmail.com"
EMAIL_PASSWORD="iwtk omvu tdio qbln"
```

5. **Initialize the database**:

```bash
python -m delete
python -m test
```

6. **Run the application**:

```bash
flask run --port=5001
```


The above code is a Flask API for a multi-tenant SaaS Auth service with features like user signup, sign-in, invite system, password reset, and stats gathering. Below are the key commands to run and test the API endpoints using `curl`:

### 1. **Run the Server**
To start the server, run the following command:
```bash
python app.py
```

### 2. **API Testing Commands**

#### Sign Up
```bash
curl -X POST http://localhost:5001/signup -H "Content-Type: application/json" -d '{"email": "user@example.com", "password": "password123", "organization_name": "MyOrg", "role": "admin"}'
```

#### Sign In
```bash
curl -X POST http://localhost:5001/signin -H "Content-Type: application/json" -d '{"email": "user@example.com", "password": "password123"}'
```

#### Reset Password Request
```bash
curl -X POST http://localhost:5001/reset_password -H "Content-Type: application/json" -d '{"email": "user@example.com", "new_password": "newpassword123"}'
```

#### Invite Member
```bash
curl -X POST http://localhost:5001/invite_member -H "Content-Type: application/json" -d '{"user_id": "1", "org_id": "1"}'
```

#### Accept Invite
```bash
curl -X GET http://localhost:5001/accept_invite?token=invite_token
```

#### Delete User, Member, and Invites
```bash
curl -X DELETE http://localhost:5001/delete -H "Content-Type: application/json" -d '{"user_id": "2", "org_id": "1"}'
```

#### Update Member Role
```bash
curl -X POST http://localhost:5001/update_member_role -H "Content-Type: application/json" -d '{"user_id": "2", "org_id": "1", "new_role_name": "admin"}'
```

#### Role-Wise Users Stats
```bash
curl -X GET http://localhost:5001/role_wise_users
```
#### Organization Role User Stats
```bash
curl -X GET "http://localhost:5001/stats/organization-role-users"
```

#### Organization-Wise User Stats 
```bash
curl -X GET "http://localhost:5001/stats/organization-users"
```
#### Organization Role User Stats (with filters)
```bash
curl -X GET "http://localhost:5001/stats/organization-role-users?from_time=1693900800&to_time=1694000800&status=0"
```

#### Organization-Wise User Stats (with filters)
```bash
curl -X GET "http://localhost:5001/stats/organization-users?from_time=1693900800&to_time=1694000800&status=0"
```

## Scheduled Jobs

The project has a scheduled job that runs every minute to delete expired invite tokens.



