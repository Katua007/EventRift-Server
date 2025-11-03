# Import Flask to create our web application
from flask import Flask, request
# Import CORS to allow cross-origin requests from frontend
from flask_cors import CORS
# Import os for environment variables and file paths
import os
# Import sys for system path manipulation
import sys
# Import logging to track what the app is doing
import logging

# Add the current directory to Python's search path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging to show info level messages and above
logging.basicConfig(level=logging.INFO)
# Create a logger for this module to track events
logger = logging.getLogger(__name__)

# Try to import our custom configuration and extensions
try:
    from eventrift.config import Config
    from eventrift.extensions import db, migrate, api, jwt
except ImportError:
    # If the custom modules aren't available, use basic Flask extensions as fallback
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate
    from flask_restful import Api
    from flask_jwt_extended import JWTManager

    # Create a basic configuration class for the app
    class Config:
        # Database connection string, defaults to local SQLite file
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///eventrift.db')
        # Don't track modifications for performance
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        # Secret key for JWT tokens
        JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-secret')
        # General secret key for Flask sessions
        SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')

    # Create database instance
    db = SQLAlchemy()
    # Create migration manager for database changes
    migrate = Migrate()
    # Create REST API manager
    api = Api()
    # Create JWT manager for authentication
    jwt = JWTManager()

# Global storage - Events data (like a simple database in memory)
events_db = [
    {
        "id": 1,
        "title": "Koroga Festival 2024",
        "date": "2024-12-15",
        "start_time": "14:00",
        "end_time": "23:00",
        "location": "Nairobi Arboretum, Nairobi",
        "venue_name": "Nairobi Arboretum",
        "address": "State House Avenue, Nairobi, Kenya",
        "category": "Music",
        "theme": "Festival",
        "ticket_price": 3500,
        "early_bird_price": 2800,
        "max_attendees": 8000,
        "tickets_sold": 2400,
        "image": "/assets/images/Koroga Festival.jpeg",
        "description": "Kenya's premier music festival featuring local and international artists",
        "rating": 4.7,
        "reviews_count": 156,
        "days_of_week": ["Sunday"]
    },
    {
        "id": 2,
        "title": "Blankets & Wine Nairobi",
        "date": "2024-12-28",
        "start_time": "13:00",
        "end_time": "20:00",
        "location": "Uhuru Gardens, Nairobi",
        "venue_name": "Uhuru Gardens",
        "address": "Langata Road, Nairobi, Kenya",
        "category": "Music",
        "theme": "Festival",
        "ticket_price": 2500,
        "early_bird_price": 2000,
        "max_attendees": 5000,
        "tickets_sold": 1800,
        "image": "/assets/images/Blankets and Wine.jpeg",
        "description": "Outdoor music festival with picnic vibes and great music",
        "rating": 4.5,
        "reviews_count": 89,
        "days_of_week": ["Saturday"]
    },
    {
        "id": 3,
        "title": "Nyege Nyege Festival Kenya",
        "date": "2025-01-18",
        "start_time": "16:00",
        "end_time": "02:00",
        "location": "Hell's Gate National Park, Naivasha",
        "venue_name": "Hell's Gate National Park",
        "address": "Naivasha, Kenya",
        "category": "Music",
        "theme": "Festival",
        "ticket_price": 4500,
        "early_bird_price": 3500,
        "max_attendees": 3000,
        "tickets_sold": 900,
        "image": "/assets/images/Nyege Nyege Festival.jpeg",
        "description": "Electronic music festival in stunning natural setting",
        "rating": 4.8,
        "reviews_count": 67,
        "days_of_week": ["Saturday"]
    }
]

services_db = [
    {'id': 1, 'name': 'Wedding Photography', 'category': 'Photography', 'price': 50000, 'vendor_id': 9905},
    {'id': 2, 'name': 'Event Catering', 'category': 'Catering', 'price': 25000, 'vendor_id': 9905}
]
notifications_db = []
ticket_bookings_db = []
users_db = {}

# Function to create and configure our Flask application
def create_app():
    # Create the main Flask application instance
    app = Flask(__name__)
    # Load configuration settings from our Config class
    app.config.from_object(Config)

    # Enable CORS (Cross-Origin Resource Sharing) so frontend can talk to backend
    allowed_origins = [
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:5174',
        'https://*.vercel.app',
        'https://event-rift-client.vercel.app',
        'https://eventrift-server.onrender.com',
    ]

    frontend_url = os.environ.get('FRONTEND_URL', 'https://event-rift-client.vercel.app')
    if frontend_url not in allowed_origins:
        allowed_origins.append(frontend_url)

    CORS(app,
         origins=allowed_origins,
         methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
         supports_credentials=True,
         expose_headers=['Content-Type', 'Authorization'])

    # Initialize Flask extensions with our app
    try:
        db.init_app(app)
        migrate.init_app(app, db)
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
    
    api.init_app(app)
    jwt.init_app(app)

    # Routes
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'message': 'EventRift API is running'}

    @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
    def login():
        if request.method == 'OPTIONS':
            return '', 204

        try:
            data = request.get_json() or {}
            email = data.get('email', 'user@example.com')
            
            username = email.split('@')[0] if '@' in email else email
            
            # Check if user exists in our database first
            if email in users_db:
                user_data = users_db[email]
                user_role = user_data['role']
                display_name = user_data['name']
            else:
                # Fallback role detection for existing users
                user_role = 'Goer'
                email_lower = email.lower()
                username_lower = username.lower()
                
                if ('organizer' in email_lower or 'organizer' in username_lower):
                    user_role = 'Organizer'
                elif ('vendor' in email_lower or 'vendor' in username_lower):
                    user_role = 'Vendor'
                
                display_name = username.replace('.', ' ').replace('_', ' ').title()

            from flask_jwt_extended import create_access_token
            access_token = create_access_token(
                identity=email,
                additional_claims={'role': user_role}
            )

            return {
                'success': True,
                'access_token': access_token,
                'user': {
                    'email': email,
                    'username': username,
                    'name': display_name,
                    'role': user_role,
                    'id': hash(email) % 10000
                }
            }
        except Exception as e:
            return {'success': False, 'message': 'Login failed'}, 401

    @app.route('/auth/profile', methods=['GET', 'OPTIONS'])
    @app.route('/api/auth/profile', methods=['GET', 'OPTIONS'])
    def get_profile():
        if request.method == 'OPTIONS':
            return '', 204

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'success': False, 'message': 'No token provided'}, 401

        return {
            'success': True,
            'user': {
                'id': 1,
                'email': 'user@example.com',
                'name': 'User Name',
                'role': 'user',
                'username': 'User Name'
            }
        }

    @app.route('/api/events', methods=['GET', 'POST', 'OPTIONS'])
    def handle_events():
        if request.method == 'OPTIONS':
            return '', 204
        
        if request.method == 'GET':
            return {'success': True, 'events': events_db}
        
        return {'success': False, 'message': 'Method not allowed'}, 405

    @app.route('/api/events/<int:event_id>', methods=['GET', 'OPTIONS'])
    def get_event(event_id):
        if request.method == 'OPTIONS':
            return '', 204
        
        event = next((e for e in events_db if e['id'] == event_id), None)
        if not event:
            return {'success': False, 'message': 'Event not found'}, 404
        
        return {'success': True, 'event': event}

    @app.route('/api/tickets/book', methods=['POST', 'OPTIONS'])
    def book_ticket():
        if request.method == 'OPTIONS':
            return '', 204

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'success': False, 'message': 'Authentication required'}, 401

        data = request.get_json()
        event_id = data.get('event_id')
        quantity = data.get('quantity', 1)
        user_email = data.get('user_email', 'test@example.com')

        event = next((e for e in events_db if e['id'] == event_id), None)
        if not event:
            return {'success': False, 'message': 'Event not found'}, 404

        total_price = event['ticket_price'] * quantity

        booking = {
            'id': len(ticket_bookings_db) + 1,
            'event_id': event_id,
            'user_email': user_email,
            'quantity': quantity,
            'total_price': total_price,
            'status': 'CONFIRMED',
            'booking_date': __import__('datetime').datetime.now().isoformat(),
            'event_title': event['title']
        }

        ticket_bookings_db.append(booking)
        event['tickets_sold'] += quantity

        return {
            'success': True,
            'message': f'Successfully booked {quantity} ticket(s)!',
            'booking': booking
        }, 201

    @app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
    def register():
        if request.method == 'OPTIONS':
            return '', 204

        try:
            data = request.get_json() or {}
            email = data.get('email', 'user@example.com')
            role = data.get('role', 'Goer')
            
            username = email.split('@')[0] if '@' in email else email
            display_name = username.replace('.', ' ').replace('_', ' ').title()

            # Store user in our database
            users_db[email] = {
                'email': email,
                'username': username,
                'name': display_name,
                'role': role,
                'id': hash(email) % 10000
            }

            from flask_jwt_extended import create_access_token
            access_token = create_access_token(
                identity=email,
                additional_claims={'role': role}
            )

            return {
                'success': True,
                'message': 'User registered successfully',
                'access_token': access_token,
                'user': {
                    'email': email,
                    'username': username,
                    'name': display_name,
                    'role': role,
                    'id': hash(email) % 10000
                }
            }, 201
        except Exception as e:
            return {'success': False, 'message': 'Registration failed'}, 400

    @app.route('/api/auth/logout', methods=['POST', 'OPTIONS'])
    def logout():
        if request.method == 'OPTIONS':
            return '', 204
        return {'success': True, 'message': 'Logged out successfully'}

    @app.route('/user/tickets', methods=['GET', 'OPTIONS'])
    @app.route('/api/tickets/user', methods=['GET', 'OPTIONS'])
    def get_user_tickets():
        if request.method == 'OPTIONS':
            return '', 204

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'success': False, 'message': 'Authentication required'}, 401

        user_bookings = [b for b in ticket_bookings_db if b['user_email'] == 'test@example.com']
        
        return {
            'success': True,
            'tickets': user_bookings,
            'upcoming_events': []
        }

    @app.route('/api/dashboard/goer', methods=['GET', 'OPTIONS'])
    def goer_dashboard():
        if request.method == 'OPTIONS':
            return '', 204

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'success': False, 'message': 'Authentication required'}, 401

        from datetime import datetime
        current_date = datetime.now()
        
        available_events = []
        for event in events_db:
            try:
                event_date = datetime.fromisoformat(event['date'])
                if event_date >= current_date:
                    available_events.append(event)
            except:
                continue

        return {
            'success': True,
            'user': {'email': 'test@example.com', 'total_spent': 0, 'total_tickets': 0},
            'upcoming_events': [],
            'past_events': [],
            'available_events': available_events,
            'stats': {
                'total_upcoming_events': 0,
                'total_past_events': 0,
                'total_bookings': 0,
                'total_spent': 0,
                'total_tickets': 0
            }
        }

    @app.route('/api/dashboard/organizer', methods=['GET', 'OPTIONS'])
    def organizer_dashboard():
        if request.method == 'OPTIONS':
            return '', 204

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'success': False, 'message': 'Authentication required'}, 401

        organizer_events = [e for e in events_db if e.get('organizer_id') == 'organizer@example.com']
        total_revenue = sum(e.get('tickets_sold', 0) * e.get('ticket_price', 0) for e in organizer_events)

        return {
            'success': True,
            'events': organizer_events,
            'total_events': len(organizer_events),
            'total_revenue': total_revenue,
            'total_tickets_sold': sum(e.get('tickets_sold', 0) for e in organizer_events)
        }

    @app.route('/api/vendor/services', methods=['GET', 'OPTIONS'])
    @app.route('/services/vendor', methods=['GET', 'OPTIONS'])
    @app.route('/user/services', methods=['GET', 'OPTIONS'])
    def get_vendor_services():
        if request.method == 'OPTIONS':
            return '', 204
        return {'success': True, 'services': services_db}

    @app.route('/services', methods=['POST', 'OPTIONS'])
    def create_service():
        if request.method == 'OPTIONS':
            return '', 204
        data = request.get_json() or {}
        service = {
            'id': len(services_db) + 1,
            'name': data.get('name'),
            'category': data.get('category'),
            'price': data.get('price'),
            'vendor_id': data.get('vendor_id', 9905)
        }
        services_db.append(service)
        return {'success': True, 'service': service}, 201

    @app.route('/api/organizer/events', methods=['GET', 'OPTIONS'])
    @app.route('/events/organizer', methods=['GET', 'OPTIONS'])
    @app.route('/user/events', methods=['GET', 'OPTIONS'])
    def get_organizer_events():
        if request.method == 'OPTIONS':
            return '', 204
        return {'success': True, 'events': events_db}

    return app

# Create the Flask application instance
app = create_app()

# Run the app if this file is executed directly
if __name__ == '__main__':
    app.run(port=5555, debug=True)