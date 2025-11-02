# Monday Presentation: EventRift Server Code Explanation

## Project Overview
EventRift Server is a Flask-based backend API for an event management platform. It handles user authentication, event creation/management, ticket booking, vendor services, and payment processing through M-Pesa integration.

---

## File Structure and Purpose

### Root Directory Files

#### 1. `app.py` - Main Application Entry Point
**Purpose**: This is the heart of the application that starts the Flask server and handles basic routing.

**Line-by-Line Explanation**:

```python
from flask import Flask, request
```
- Imports Flask framework for creating web applications
- Imports request object to handle HTTP requests (GET, POST, etc.)

```python
from flask_cors import CORS
```
- Imports CORS (Cross-Origin Resource Sharing) to allow frontend applications from different domains to access this API

```python
import os
import sys
import logging
```
- `os`: Access operating system environment variables
- `sys`: System-specific parameters and functions
- `logging`: Create log messages for debugging

```python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```
- Adds the current directory to Python's path so it can find our custom modules

```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```
- Sets up logging to show INFO level messages and above
- Creates a logger instance for this file

```python
try:
    from eventrift.config import Config
    from eventrift.extensions import db, migrate, api, jwt
except ImportError:
    # Fallback code if eventrift package isn't available
```
- Tries to import our custom configuration and database extensions
- If import fails, creates fallback versions

**CORS Configuration Section**:
```python
allowed_origins = [
    'http://localhost:3000',      # React dev server
    'http://localhost:5173',      # Vite dev server
    'http://localhost:5174',      # Alternative Vite port
    'https://*.vercel.app',       # Vercel deployments
    'https://event-rift-client.vercel.app',  # Production frontend
]
```
- Lists all the frontend URLs that are allowed to make requests to this API
- Includes development servers and production deployment

```python
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
```
- This function runs before every request
- OPTIONS requests are "preflight" requests that browsers send to check if they're allowed to make the actual request

**Event Management Routes**:
```python
@app.route('/events', methods=['GET', 'POST', 'OPTIONS'])
def handle_events():
```
- Creates an endpoint at `/events` that accepts GET (retrieve), POST (create), and OPTIONS (preflight) requests
- When users visit this URL, this function runs

```python
if request.method == 'GET':
    return {'success': True, 'events': events_db}
```
- If someone makes a GET request, return all events from the database

```python
if request.method == 'POST':
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return {'success': False, 'message': 'Authentication required'}, 401
```
- If someone tries to create an event (POST), check if they're logged in
- Return error 401 (Unauthorized) if no authentication token provided

#### 2. `wsgi.py` - Web Server Gateway Interface
**Purpose**: This file is used by production web servers (like Gunicorn) to run the application.

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```
- Ensures the web server can find all our application files

```python
import app as app_module
app = app_module.app
```
- Imports our main application and makes it available to the web server

#### 3. `requirements.txt` - Dependencies List
**Purpose**: Lists all the Python packages needed to run this application.

```
Flask==3.1.2                 # Main web framework
Flask-RESTful==0.3.10        # REST API extensions
Flask-SQLAlchemy==3.1.1      # Database ORM (Object Relational Mapping)
Flask-Migrate==4.1.0         # Database migration tools
Flask-JWT-Extended==4.7.1    # JWT token authentication
Flask-SocketIO==5.4.1        # Real-time communication
Flask-CORS==5.0.0            # Cross-origin resource sharing
psycopg2-binary==2.9.11      # PostgreSQL database driver
marshmallow==4.0.1           # Data serialization/validation
python-dotenv==1.1.1         # Environment variable loading
gunicorn==23.0.0             # Production web server
flasgger==0.9.7.1            # API documentation
cloudinary==1.44.1           # Image upload service
```

#### 4. `render.yaml` - Deployment Configuration
**Purpose**: Tells Render (hosting platform) how to deploy the application.

```yaml
services:
  - type: web                           # This is a web service
    name: eventrift-server              # Service name
    runtime: python                     # Use Python runtime
    buildCommand: "pip install -r requirements.txt"  # Install dependencies
    startCommand: "gunicorn wsgi:app"   # Start the server
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.4                   # Use Python 3.11.4
      - key: FRONTEND_URL
        value: https://event-rift-client.vercel.app  # Frontend URL for CORS
```

---

## EventRift Package Structure

### Configuration Files

#### 1. `eventrift/config.py` - Application Configuration
**Purpose**: Centralizes all configuration settings for the application.

```python
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
```
- Tries to load environment variables from a `.env` file
- If dotenv package isn't available, continues without it

```python
class Config:
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
```
- Gets database URL from environment variables
- Fixes compatibility issue with newer PostgreSQL drivers

```python
if DATABASE_URL:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
else:
    try:
        import psycopg2
        SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost:5432/eventrift_dev'
    except ImportError:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///eventrift.db'
```
- Uses PostgreSQL if available, otherwise falls back to SQLite for development

**M-Pesa Payment Configuration**:
```python
MPESA_BASE_URL = os.environ.get('MPESA_BASE_URL', 'https://sandbox.safaricom.co.ke')
CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', 'YOUR_CONSUMER_KEY_HERE')
CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', 'YOUR_CONSUMER_SECRET_HERE')
```
- Configuration for Safaricom's M-Pesa mobile payment system
- Uses sandbox (testing) environment by default

**Cloudinary Configuration**:
```python
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
```
- Configuration for Cloudinary image hosting service
- Used to store and serve event images

#### 2. `eventrift/extensions.py` - Flask Extensions
**Purpose**: Initializes all Flask extensions in one place.

```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_jwt_extended import JWTManager
```
- Imports all the Flask extensions we need

```python
db = SQLAlchemy()           # Database ORM
migrate = Migrate()         # Database migrations
api = Api()                 # REST API framework
jwt = JWTManager()          # JWT authentication
```
- Creates instances of each extension

```python
try:
    from flask_socketio import SocketIO
    socketio = SocketIO(cors_allowed_origins="*")
except ImportError:
    socketio = None
```
- Optionally imports SocketIO for real-time features
- Sets CORS to allow all origins for WebSocket connections

---

### Database Models

#### 1. `eventrift/models/user.py` - User Model
**Purpose**: Defines the structure of user data in the database.

```python
from eventrift.extensions import db
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
```
- Imports database instance and password hashing utilities

```python
class User(db.Model):
    __tablename__ = 'users'
```
- Creates a User class that represents a database table named 'users'

```python
id = db.Column(db.Integer, primary_key=True)
email = db.Column(db.String(100), unique=True, nullable=False)
username = db.Column(db.String(50), nullable=False)
_password_hash = db.Column(db.String(255), nullable=False)
role = db.Column(db.String(20), nullable=False, default='Goer')
```
- Defines database columns:
  - `id`: Unique identifier for each user
  - `email`: User's email (must be unique)
  - `username`: Display name
  - `_password_hash`: Encrypted password (private)
  - `role`: User type (Goer, Organizer, Vendor, etc.)

```python
@hybrid_property
def password_hash(self):
    return self._password_hash

@password_hash.setter
def password_hash(self, password):
    self._password_hash = generate_password_hash(password)
```
- Creates a property that automatically encrypts passwords when set
- Never stores plain text passwords for security

```python
def check_password(self, password):
    return check_password_hash(self._password_hash, password)
```
- Method to verify if a provided password matches the stored hash

#### 2. `eventrift/models/event.py` - Event Model
**Purpose**: Defines the structure of event data in the database.

```python
class Event(db.Model):
    __tablename__ = 'events'
```
- Creates an Event class representing the 'events' table

```python
id = db.Column(db.Integer, primary_key=True)
organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
name = db.Column(db.String(100), nullable=False)
description = db.Column(db.Text, nullable=False)
location = db.Column(db.String(200), nullable=False)
date_time = db.Column(db.DateTime, nullable=False)
ticket_price = db.Column(db.Numeric(10, 2), nullable=False)
capacity = db.Column(db.Integer, nullable=False)
```
- Event properties:
  - `organizer_id`: Links to the user who created the event
  - `name`: Event title
  - `description`: Detailed event information
  - `location`: Where the event takes place
  - `date_time`: When the event happens
  - `ticket_price`: Cost per ticket (up to 99,999,999.99)
  - `capacity`: Maximum number of attendees

```python
image_url = db.Column(db.String(500), nullable=True)
is_published = db.Column(db.Boolean, default=False)
status = db.Column(db.String(20), default='Active', nullable=False)
```
- Additional properties:
  - `image_url`: Link to event poster/image
  - `is_published`: Whether event is visible to public
  - `status`: Active, Inactive, or Cancelled

```python
def save(self):
    db.session.add(self)
    db.session.commit()

def delete(self):
    db.session.delete(self)
    db.session.commit()
```
- Helper methods to save or delete events from database

---

### API Routes

#### 1. `eventrift/routes/__init__.py` - Route Initialization
**Purpose**: Registers all API routes with the Flask application.

```python
def initialize_routes(app):
    """Initialize all routes for the Flask app"""
```
- Main function that sets up all API endpoints

```python
from eventrift.routes.auth_routes import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
```
- Imports authentication routes and registers them under `/auth` prefix
- All auth routes will start with `/auth/` (e.g., `/auth/login`)

```python
try:
    from eventrift.routes.event_routes import events_bp
    app.register_blueprint(events_bp, url_prefix='/api')
except ImportError:
    pass
```
- Tries to register event routes under `/api` prefix
- If import fails, continues without error (graceful degradation)

#### 2. `eventrift/routes/auth_routes.py` - Authentication Routes
**Purpose**: Handles user login, registration, and profile management.

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
```
- Imports Flask Blueprint for organizing routes
- Imports JWT functions for token-based authentication

```python
auth_bp = Blueprint('auth', __name__)
```
- Creates a Blueprint named 'auth' to group authentication routes

```python
@auth_bp.route('/login', methods=['POST'])
def login():
```
- Creates a login endpoint that accepts POST requests
- URL will be `/auth/login` when registered with the app

```python
data = request.get_json()
email = data.get('email')
password = data.get('password')
```
- Gets JSON data from the request body
- Extracts email and password from the data

```python
if email and password:
    access_token = create_access_token(
        identity=email,
        additional_claims={'role': 'user'}
    )
```
- If both email and password are provided, creates a JWT token
- Token contains the user's email and role

```python
return {
    'success': True,
    'access_token': access_token,
    'user': {
        'email': email,
        'role': 'user'
    }
}, 200
```
- Returns success response with token and user info
- HTTP status 200 means "OK"

```python
@auth_bp.route('/register', methods=['POST'])
def register():
```
- Creates a registration endpoint for new users

```python
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
```
- Creates a profile endpoint that requires authentication
- `@jwt_required()` decorator ensures user is logged in

```python
current_user = get_jwt_identity()
```
- Gets the current user's identity from their JWT token

#### 3. `eventrift/routes/event_routes.py` - Event Management Routes
**Purpose**: Handles creating, reading, updating, and deleting events.

```python
from flask import Blueprint, request
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
```
- Imports necessary Flask and authentication components

```python
events_bp = Blueprint('events_bp', __name__)
api = Api(events_bp)
```
- Creates a Blueprint for event routes
- Creates an API instance for RESTful endpoints

```python
class EventListResource(Resource):
```
- Creates a REST resource class for handling multiple events

```python
def get(self):
    """Public route: List all active events with pagination."""
```
- GET method to retrieve list of events
- Public means no authentication required

```python
page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 12, type=int)
```
- Gets pagination parameters from URL query string
- Default: page 1, 12 events per page

```python
if per_page > 50:
    per_page = 50
```
- Limits maximum events per page to prevent server overload

```python
pagination = Event.query.filter_by(status='Active').paginate(
    page=page, 
    per_page=per_page, 
    error_out=False
)
```
- Queries database for active events with pagination
- `error_out=False` returns empty page instead of error if page doesn't exist

```python
@jwt_required()
def post(self):
    """Creates a new event, handling optional Cloudinary image upload."""
```
- POST method to create new events
- Requires authentication (user must be logged in)

```python
current_user_id = get_jwt_identity()
```
- Gets the ID of the currently logged-in user

```python
if isinstance(current_user_id, str):
    try:
        current_user_id = int(current_user_id)
    except ValueError:
        # Try to find user by email
```
- JWT might return user ID as string or email
- Converts to integer ID or looks up user by email

```python
image_file = request.files.get('image')
```
- Gets uploaded image file from the request

```python
if request.form:
    if 'data' in request.form:
        try:
            event_data.update(json.loads(request.form['data']))
        except json.JSONDecodeError:
            return {'message': 'Invalid JSON data provided in the form field.'}, 400
```
- Handles form data (when image is uploaded)
- Event data might be sent as JSON string in 'data' field

```python
# Transform field names and data types
if 'title' in event_data and event_data['title']:
    transformed_data['name'] = event_data['title']
```
- Frontend sends 'title', but database expects 'name'
- Transforms frontend data format to match database schema

```python
if 'start_date' in event_data and 'start_time' in event_data:
    date_str = event_data['start_date']
    time_str = event_data['start_time']
    transformed_data['date_time'] = f"{date_str}T{time_str}:00"
```
- Combines separate date and time fields into single datetime

```python
if image_file and CLOUDINARY_AVAILABLE:
    image_url = upload_event_image(image_file)
```
- Uploads image to Cloudinary if file provided and service available

```python
validated_data = event_schema.load(event_data)
```
- Validates event data using Marshmallow schema
- Ensures all required fields are present and correctly formatted

```python
new_event = Event(
    name=validated_data['name'],
    description=validated_data['description'],
    location=validated_data['location'],
    date_time=validated_data['date_time'],
    ticket_price=validated_data['ticket_price'],
    capacity=validated_data['capacity'],
    image_url=validated_data.get('image_url'),
    organizer_id=current_user_id
)
```
- Creates new Event object with validated data

```python
new_event.save()
```
- Saves the event to the database

```python
class OrganizerEventsResource(Resource):
    @jwt_required()
    def get(self):
```
- Resource for organizers to view their own events
- Requires authentication

```python
events = Event.query.filter_by(organizer_id=current_user_id).all()
```
- Gets all events created by the current user

```python
api.add_resource(EventListResource, '/events')
api.add_resource(OrganizerEventsResource, '/organizers/events')
```
- Registers the resource classes with specific URL endpoints

---

### Schemas (Data Validation)

Schemas use Marshmallow library to validate and serialize data between the API and database.

#### Purpose of Schemas:
1. **Validation**: Ensure incoming data is correct format
2. **Serialization**: Convert database objects to JSON for API responses
3. **Deserialization**: Convert JSON to database objects
4. **Documentation**: Define what fields are required/optional

---

### Utility Functions

#### 1. `eventrift/utils/cloudinary_upload.py` - Image Upload
**Purpose**: Handles uploading event images to Cloudinary service.

#### 2. `eventrift/utils/daraja_api.py` - M-Pesa Integration
**Purpose**: Integrates with Safaricom's Daraja API for mobile payments.

#### 3. `eventrift/utils/email_service.py` - Email Notifications
**Purpose**: Sends email notifications using SendGrid service.

---

## Key Features Explained

### 1. Authentication System
- **JWT Tokens**: Secure, stateless authentication
- **Role-Based Access**: Different permissions for Goers, Organizers, Vendors
- **Password Hashing**: Secure password storage using Werkzeug

### 2. Event Management
- **CRUD Operations**: Create, Read, Update, Delete events
- **Image Upload**: Integration with Cloudinary for event posters
- **Pagination**: Efficient loading of large event lists
- **Status Management**: Active, Inactive, Cancelled events

### 3. Payment Processing
- **M-Pesa Integration**: Mobile money payments through Daraja API
- **Ticket Purchases**: Secure payment processing for event tickets
- **Stall Bookings**: Vendor stall rental payments

### 4. Database Design
- **PostgreSQL**: Production database with full SQL features
- **SQLite**: Development database for easy setup
- **Migrations**: Version control for database schema changes
- **Relationships**: Proper foreign key relationships between tables

### 5. API Design
- **RESTful**: Standard HTTP methods (GET, POST, PUT, DELETE)
- **JSON**: All data exchange in JSON format
- **CORS**: Proper cross-origin resource sharing for web apps
- **Error Handling**: Consistent error responses with proper HTTP status codes

### 6. Development Features
- **Environment Variables**: Secure configuration management
- **Logging**: Comprehensive logging for debugging
- **Fallback Systems**: Graceful degradation when services unavailable
- **Docker Ready**: Can be containerized for deployment

---

## Frontend Integration Points

### 1. Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/register` - User registration  
- `GET /auth/profile` - Get user profile

### 2. Event Endpoints
- `GET /api/events` - List all events (public)
- `POST /api/events` - Create new event (authenticated)
- `GET /api/organizers/events` - Get organizer's events (authenticated)

### 3. CORS Configuration
- Allows requests from localhost (development)
- Allows requests from Vercel (production)
- Supports credentials (cookies/tokens)
- Handles preflight OPTIONS requests

---

## Deployment Architecture

### 1. Render Platform
- **Web Service**: Hosts the Flask application
- **PostgreSQL**: Managed database service
- **Environment Variables**: Secure configuration storage

### 2. External Services
- **Cloudinary**: Image hosting and processing
- **SendGrid**: Email delivery service
- **Safaricom Daraja**: M-Pesa payment processing

### 3. Frontend Integration
- **Vercel**: Frontend hosting platform
- **CORS**: Secure cross-origin communication
- **JWT**: Stateless authentication tokens

---

## Security Features

### 1. Authentication Security
- **Password Hashing**: Never store plain text passwords
- **JWT Tokens**: Secure, time-limited access tokens
- **Role-Based Access**: Different permissions per user type

### 2. API Security
- **CORS**: Controlled cross-origin access
- **Input Validation**: All data validated before processing
- **SQL Injection Prevention**: ORM prevents direct SQL injection

### 3. Environment Security
- **Environment Variables**: Sensitive data not in code
- **Secret Keys**: Unique keys for JWT and Flask sessions
- **HTTPS**: Encrypted communication in production

---

## Error Handling Strategy

### 1. HTTP Status Codes
- **200**: Success
- **201**: Created successfully
- **400**: Bad request (invalid data)
- **401**: Unauthorized (login required)
- **404**: Not found
- **422**: Validation error
- **500**: Server error

### 2. Consistent Response Format
```json
{
    "success": true/false,
    "message": "Human readable message",
    "data": {...} // Optional data
}
```

### 3. Graceful Degradation
- Fallback to basic functionality if advanced features fail
- Continue operation even if optional services unavailable
- Comprehensive logging for debugging

---

This presentation covers every major component of the EventRift Server, explaining what each file does, why it exists, and how it contributes to the overall application functionality. The code is designed to be modular, secure, and scalable for a production event management platform.