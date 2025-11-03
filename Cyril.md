# EventRift Server Implementation Documentation

## Overview
This document details all the code implemented to achieve the EventRift server goals:
1. Backend Repository Setup with modular Flask structure
2. Database & Model Setup with PostgreSQL/SQLite
3. JWT Authentication implementation
4. WebSockets for real-time features
5. Swagger/OpenAPI documentation and deployment configuration

---

## 1. Backend Repository Setup

### 1.1 Project Structure Creation

**File: `requirements.txt`**
```python
Flask==3.1.2
Flask-RESTful==0.3.10
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.1.0
Flask-JWT-Extended==4.7.1
Flask-SocketIO==5.4.1
Flask-CORS==5.0.0
marshmallow==4.0.1
python-dotenv==1.1.1
gunicorn==23.0.0
flasgger==0.9.7.1
cloudinary==1.44.1
```

**Purpose**: Defines all Python dependencies needed for the Flask application
- `Flask==3.1.2`: Core web framework for building the API
- `Flask-RESTful==0.3.10`: Extension for building REST APIs easily
- `Flask-SQLAlchemy==3.1.1`: ORM for database operations
- `Flask-Migrate==4.1.0`: Database migration management
- `Flask-JWT-Extended==4.7.1`: JWT token authentication
- `Flask-SocketIO==5.4.1`: WebSocket support for real-time features
- `Flask-CORS==5.0.0`: Cross-Origin Resource Sharing for frontend communication
- `marshmallow==4.0.1`: Data serialization and validation
- `python-dotenv==1.1.1`: Environment variable management
- `gunicorn==23.0.0`: Production WSGI server
- `flasgger==0.9.7.1`: Swagger/OpenAPI documentation
- `cloudinary==1.44.1`: Image upload and management service

### 1.2 Configuration Setup

**File: `eventrift/config.py`**
```python
import os

# Optional dotenv import - only load if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, environment variables should be set by the deployment platform
    pass

class Config:
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Use SQLite as fallback for local development when PostgreSQL isn't available
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Always use SQLite for simplicity - no PostgreSQL dependency issues
        SQLALCHEMY_DATABASE_URI = 'sqlite:///eventrift.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-super-secret-key-change-me')
    
    # Other Configs
    SECRET_KEY = os.environ.get('SECRET_KEY', 'another-default-secret')
```

**Purpose**: Centralized configuration management
- `load_dotenv()`: Loads environment variables from .env file for development
- `DATABASE_URL`: Gets database connection string from environment, with PostgreSQL URL fix for Render deployment
- `SQLALCHEMY_DATABASE_URI`: Falls back to SQLite if PostgreSQL not available
- `SQLALCHEMY_TRACK_MODIFICATIONS = False`: Disables modification tracking for performance
- `JWT_SECRET_KEY`: Secret key for JWT token signing and verification
- `SECRET_KEY`: Flask's built-in secret key for session management

### 1.3 Extensions Setup

**File: `eventrift/extensions.py`**
```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
api = Api()
jwt = JWTManager()

# Optional SocketIO import - only initialize if available
try:
    from flask_socketio import SocketIO
    socketio = SocketIO(cors_allowed_origins="*")
except ImportError:
    socketio = None
```

**Purpose**: Initializes Flask extensions for modular use
- `db = SQLAlchemy()`: Database ORM instance for model definitions
- `migrate = Migrate()`: Database migration manager for schema changes
- `api = Api()`: REST API manager for resource-based endpoints
- `jwt = JWTManager()`: JWT authentication manager
- `socketio = SocketIO(cors_allowed_origins="*")`: WebSocket manager with CORS enabled for real-time features
- Try/except blocks ensure graceful degradation if optional dependencies aren't available

---

## 2. Database & Model Setup

### 2.1 User Model

**File: `eventrift/models/user.py`**
```python
from eventrift.extensions import db
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    _password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Goer') # Role-Based Access Control
    
    # Vendor specific fields
    license_number = db.Column(db.String(50))
    
    # Email verification
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    @hybrid_property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
```

**Purpose**: Defines the User model with authentication and role-based access
- `__tablename__ = 'users'`: Specifies database table name
- `id`: Primary key for unique user identification
- `email`: Unique email address for login (with unique constraint)
- `username`: Display name for the user
- `_password_hash`: Stores hashed password (private attribute)
- `role`: User role for access control (Goer, Organizer, Vendor, Admin)
- `license_number`: Optional field for vendor licensing
- `is_verified`: Email verification status
- `verification_token`: Token for email verification process
- `created_at`: Timestamp of user registration
- `@hybrid_property password_hash`: Property decorator for secure password handling
- `password_hash.setter`: Automatically hashes passwords when set
- `check_password()`: Verifies password against stored hash

### 2.2 Event Model

**File: `eventrift/models/event.py`**
```python
from datetime import datetime
from eventrift.extensions import db

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False) # Store date and time together
    ticket_price = db.Column(db.Numeric(10, 2), nullable=False) # Price in KES
    capacity = db.Column(db.Integer, nullable=False)

    image_url = db.Column(db.String(500), nullable=True) # Optional image link
    is_published = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='Active', nullable=False)  # Active, Inactive, Cancelled

    # Add category relationship
    category_id = db.Column(db.Integer, db.ForeignKey('event_categories.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Event {self.name}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
```

**Purpose**: Defines the Event model for event management
- `organizer_id`: Foreign key linking to the user who created the event
- `name`: Event title/name
- `description`: Detailed event description
- `location`: Event venue/location
- `date_time`: Combined date and time for the event
- `ticket_price`: Price in Kenyan Shillings (Numeric for precision)
- `capacity`: Maximum number of attendees
- `image_url`: Optional event image URL
- `is_published`: Whether event is visible to public
- `status`: Event status (Active, Inactive, Cancelled)
- `category_id`: Foreign key for event categorization
- `created_at/updated_at`: Timestamps for tracking changes
- `save()`: Convenience method to save event to database
- `delete()`: Convenience method to remove event from database

### 2.3 Database Migration

**File: `migrations/versions/6c1cb268b5c4_initial_migration.py`**
```python
def upgrade():
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('_password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('license_number', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    
    # Create events table
    op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organizer_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('location', sa.String(length=200), nullable=False),
    sa.Column('date_time', sa.DateTime(), nullable=False),
    sa.Column('ticket_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('capacity', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(length=500), nullable=True),
    sa.Column('is_published', sa.Boolean(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['organizer_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
```

**Purpose**: Database migration script to create initial tables
- Creates `users` table with all user-related columns and constraints
- Creates `events` table with foreign key relationship to users
- Establishes primary keys, unique constraints, and foreign key relationships
- Sets up proper data types for each column (String, Integer, DateTime, Numeric, Boolean)
- Ensures referential integrity between users and events tables

---

## 3. JWT Authentication Implementation

### 3.1 Authentication Routes

**File: `eventrift/routes/auth_routes.py`**
```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint for frontend"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'success': False, 'message': 'Email and password required'}, 400

        # Find user in database
        from eventrift.models.user import User
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            access_token = create_access_token(
                identity=user.id,
                additional_claims={'role': user.role}
            )
            return {
                'success': True,
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'role': user.role
                }
            }, 200

        return {'success': False, 'message': 'Invalid email or password'}, 401

    except Exception as e:
        print(f"Login error: {e}")
        return {'success': False, 'message': 'Internal server error'}, 500
```

**Purpose**: Handles user authentication with JWT tokens
- `@auth_bp.route('/login', methods=['POST'])`: Defines POST endpoint for login
- `request.get_json()`: Extracts JSON data from request body
- `User.query.filter_by(email=email).first()`: Finds user by email in database
- `user.check_password(password)`: Verifies password using hashed comparison
- `create_access_token()`: Generates JWT token with user ID and role claims
- Returns success response with token and user info, or error message
- Exception handling prevents server crashes and logs errors

### 3.2 User Registration

```python
@auth_bp.route('/register', methods=['POST'])
def register():
    """Register endpoint for frontend"""
    try:
        from eventrift.models.user import User
        from eventrift.extensions import db
        
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        username = data.get('username') or data.get('name')
        role = data.get('role', 'Goer')

        if not email or not password or not username:
            return {'success': False, 'message': 'Email, password, and username are required'}, 400

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return {'success': False, 'message': 'Email already registered'}, 409

        # Create new user
        new_user = User(
            email=email,
            username=username,
            role=role,
            password_hash=password  # This will be hashed by the setter
        )
        
        db.session.add(new_user)
        db.session.commit()

        # Create access token
        access_token = create_access_token(
            identity=new_user.id,
            additional_claims={'role': new_user.role}
        )

        return {
            'success': True,
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'username': new_user.username,
                'role': new_user.role
            }
        }, 201

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return {'success': False, 'message': 'Registration failed'}, 500
```

**Purpose**: Handles new user registration
- Validates required fields (email, password, username)
- Checks for existing users to prevent duplicates
- Creates new User instance with hashed password
- Commits to database with rollback on error
- Generates JWT token for immediate login after registration
- Returns 201 status for successful creation

### 3.3 Protected Route Example

```python
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Get current user info"""
    try:
        from eventrift.models.user import User
        
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return {'success': False, 'message': 'User not found'}, 404
        
        return {
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role,
                'license_number': user.license_number
            }
        }, 200
    except Exception as e:
        print(f"Profile error: {e}")
        return {'success': False, 'message': 'Internal server error'}, 500
```

**Purpose**: Demonstrates JWT protection for routes
- `@jwt_required()`: Decorator that requires valid JWT token
- `get_jwt_identity()`: Extracts user ID from JWT token
- Returns user profile information for authenticated users
- Provides example of how to protect sensitive endpoints

---

## 4. WebSockets Implementation

### 4.1 SocketIO Setup in Extensions

**File: `eventrift/extensions.py` (WebSocket portion)**
```python
# Optional SocketIO import - only initialize if available
try:
    from flask_socketio import SocketIO
    socketio = SocketIO(cors_allowed_origins="*")
except ImportError:
    socketio = None
```

**Purpose**: Conditional WebSocket setup
- `SocketIO(cors_allowed_origins="*")`: Enables WebSocket with CORS for all origins
- Try/except ensures app works even if SocketIO not installed
- `socketio = None` fallback prevents import errors

### 4.2 WebSocket Integration in Main App

**File: `app.py` (WebSocket portion)**
```python
# Initialize Flask extensions with our app
try:
    from eventrift.extensions import socketio
    if socketio:
        socketio.init_app(app, cors_allowed_origins="*")
        print("SocketIO initialized successfully")
except ImportError:
    print("SocketIO not available, skipping WebSocket features")
```

**Purpose**: Integrates WebSocket with Flask app
- Conditionally initializes SocketIO if available
- Enables CORS for WebSocket connections
- Graceful degradation if WebSocket features not needed

---

## 5. Route Management System

### 5.1 Route Initialization

**File: `eventrift/routes/__init__.py`**
```python
def initialize_routes(app):
    """Initialize all routes for the Flask app"""
    try:
        from eventrift.routes.auth_routes import auth_bp
        # Register auth blueprint
        app.register_blueprint(auth_bp, url_prefix='/auth')
        print("Auth blueprint registered successfully")
    except Exception as e:
        print(f"Failed to register auth blueprint: {e}")

    try:
        from eventrift.routes.event_routes import events_bp
        app.register_blueprint(events_bp, url_prefix='/api')
    except ImportError:
        pass

    # Additional route registrations...
```

**Purpose**: Centralized route registration system
- `app.register_blueprint()`: Registers route blueprints with URL prefixes
- Try/except blocks ensure graceful handling of missing route modules
- Modular approach allows easy addition/removal of route groups
- URL prefixes organize API endpoints logically

---

## 6. Deployment Configuration

### 6.1 Render Deployment

**File: `render.yaml`**
```yaml
services:
  - type: web
    name: eventrift-server
    runtime: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn wsgi:app"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.4
      - key: FRONTEND_URL
        value: https://event-rift-client.vercel.app
```

**Purpose**: Render platform deployment configuration
- `type: web`: Specifies web service deployment
- `runtime: python`: Uses Python runtime environment
- `buildCommand`: Installs dependencies from requirements.txt
- `startCommand`: Starts app using Gunicorn WSGI server
- `envVars`: Sets environment variables for production

### 6.2 WSGI Entry Point

**File: `wsgi.py`**
```python
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from the app.py file directly
import app as app_module

app = app_module.app

if __name__ == "__main__":
    app.run()
```

**Purpose**: WSGI server entry point for production
- `sys.path.insert()`: Ensures Python can find application modules
- Imports the Flask app instance from main app.py file
- Provides entry point for Gunicorn and other WSGI servers
- Allows direct execution for development testing

---

## 7. M-Pesa Payment Integration

### 7.1 Daraja API Implementation

**File: `eventrift/utils/daraja_api.py`**
```python
import requests
import base64
from datetime import datetime, timedelta

class DarajaAPI:
    """Handles M-Pesa Daraja API integration"""
    
    _access_token = None
    _token_expiry = None

    def _generate_access_token(self):
        """Generates a new access token using Consumer Key and Secret."""
        
        if DarajaAPI._access_token and DarajaAPI._token_expiry and datetime.now() < DarajaAPI._token_expiry:
            return DarajaAPI._access_token

        key_secret = f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode('utf-8')
        encoded_auth = base64.b64encode(key_secret).decode('utf-8')
        
        token_url = f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
        
        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(token_url, headers=headers)
            data = response.json()
            
            if 'access_token' in data:
                DarajaAPI._access_token = data['access_token']
                DarajaAPI._token_expiry = datetime.now() + timedelta(seconds=3500)
                return DarajaAPI._access_token
        except requests.exceptions.RequestException as e:
            print(f"Token generation error: {e}")
            return None

    def stk_push_initiate(self, amount: float, phone_number: str, account_ref: str, transaction_desc: str):
        """Initiates STK Push transaction"""
        token = self._generate_access_token()
        if not token:
            return {"success": False, "message": "Failed to get M-Pesa access token."}
        
        password, timestamp = self._generate_password()
        
        # Format phone number
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        
        payload = {
            "BusinessShortCode": BUSINESS_SHORT_CODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": TRANSACTION_TYPE,
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": BUSINESS_SHORT_CODE,
            "PhoneNumber": phone_number,
            "CallBackURL": CALLBACK_URL,
            "AccountReference": account_ref,
            "TransactionDesc": transaction_desc
        }

        # Make STK Push request...
```

**Purpose**: M-Pesa payment integration
- `_generate_access_token()`: Gets OAuth token from Safaricom API
- Token caching with expiry to avoid unnecessary API calls
- `stk_push_initiate()`: Initiates mobile money payment request
- Phone number formatting for Kenyan numbers
- Proper error handling for network requests

---

## Summary

This implementation provides:

1. **Modular Flask Structure**: Organized into models, routes, utils, and config modules
2. **Database Integration**: SQLAlchemy models with PostgreSQL/SQLite support
3. **JWT Authentication**: Secure token-based authentication with role-based access
4. **WebSocket Support**: Real-time features using Flask-SocketIO
5. **Payment Integration**: M-Pesa Daraja API for mobile payments
6. **Deployment Ready**: Render.com configuration with Gunicorn WSGI server
7. **Error Handling**: Comprehensive exception handling throughout
8. **CORS Support**: Cross-origin requests enabled for frontend integration

Each component is designed for scalability, maintainability, and production deployment.