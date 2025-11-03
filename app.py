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

# Function to create and configure our Flask application
def create_app():
    # Create the main Flask application instance
    app = Flask(__name__)
    # Load configuration settings from our Config class
    app.config.from_object(Config)

    # Enable CORS (Cross-Origin Resource Sharing) so frontend can talk to backend
    # Allow multiple origins for development and production environments
    allowed_origins = [
        'http://localhost:3000',      # React development server
        'http://localhost:5173',      # Vite development server
        'http://localhost:5174',      # Alternative Vite port
        'https://*.vercel.app',       # Vercel deployment platform
        'https://event-rift-client.vercel.app',  # Production frontend
        'https://eventrift-server.onrender.com',  # Production backend
    ]

    # Get frontend URL from environment variable or use default
    frontend_url = os.environ.get('FRONTEND_URL', 'https://event-rift-client.vercel.app')
    # Add the frontend URL to allowed origins if not already there
    if frontend_url not in allowed_origins:
        allowed_origins.append(frontend_url)

    # Configure CORS with proper preflight handling for browser security
    CORS(app,
           origins=allowed_origins,  # Use specific allowed origins
           methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
           allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
           supports_credentials=True,  # Allow cookies and auth headers
           expose_headers=['Content-Type', 'Authorization'])

    # Initialize Flask extensions with our app
    try:
        db.init_app(app)        # Database
        migrate.init_app(app, db)  # Database migrations
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
        # Continue without database for fallback functionality
    
    api.init_app(app)       # REST API
    jwt.init_app(app)       # JWT authentication

    # Initialize routes from our routes module
    try:
        from eventrift.routes import initialize_routes
        initialize_routes(app)
        logger.info("Blueprint routes initialized successfully")
    except ImportError as e:
        # Skip if routes module not available (fallback routes will be used)
        logger.warning(f"Blueprint routes not available: {e}")
        pass

    # Global storage - Events data (like a simple database in memory)
    # This contains all the event information that would normally be in a real database
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
  },
  {
    "id": 4,
    "title": "Sauti za Busara Nairobi",
    "date": "2025-02-08",
    "start_time": "18:00",
    "end_time": "23:30",
    "location": "Kenya National Theatre, Nairobi",
    "venue_name": "Kenya National Theatre",
    "address": "Harry Thuku Road, Nairobi, Kenya",
    "category": "Music",
    "theme": "Cultural",
    "ticket_price": 2000,
    "max_attendees": 1200,
    "tickets_sold": 450,
    "image": "/assets/images/Sauti za Busara Festival.jpeg",
    "description": "Celebrating African music and cultural heritage",
    "rating": 4.6,
    "reviews_count": 34,
    "days_of_week": ["Saturday"]
  },
  {
    "id": 5,
    "title": "TechCrunch Startup Battlefield Africa",
    "date": "2025-01-25",
    "start_time": "08:00",
    "end_time": "18:00",
    "location": "KICC, Nairobi",
    "venue_name": "Kenyatta International Convention Centre",
    "address": "Harambee Avenue, Nairobi, Kenya",
    "category": "Technology",
    "theme": "Conference",
    "ticket_price": 8500,
    "early_bird_price": 6500,
    "max_attendees": 2000,
    "tickets_sold": 1200,
    "image": "/assets/images/TechCrunch .jpeg",
    "description": "Premier startup competition and tech conference in Africa",
    "rating": 4.9,
    "reviews_count": 78,
    "days_of_week": ["Saturday"]
  },
  {
    "id": 6,
    "title": "AI & Machine Learning Summit Kenya",
    "date": "2025-02-15",
    "start_time": "09:00",
    "end_time": "17:00",
    "location": "Strathmore University, Nairobi",
    "venue_name": "Strathmore University",
    "address": "Ole Sangale Road, Nairobi, Kenya",
    "category": "Technology",
    "theme": "Conference",
    "ticket_price": 5500,
    "early_bird_price": 4200,
    "max_attendees": 800,
    "tickets_sold": 320,
    "image": "/assets/images/AI & Machine Learning Summit Kenya.jpeg",
    "description": "Exploring the future of AI and ML in Africa",
    "rating": 4.7,
    "reviews_count": 45,
    "days_of_week": ["Saturday"]
  },
  {
    "id": 7,
    "title": "DevFest Nairobi 2025",
    "date": "2025-03-22",
    "start_time": "08:30",
    "end_time": "18:00",
    "location": "University of Nairobi, Nairobi",
    "venue_name": "University of Nairobi",
    "address": "University Way, Nairobi, Kenya",
    "category": "Technology",
    "theme": "Workshop",
    "ticket_price": 0,
    "max_attendees": 1500,
    "tickets_sold": 890,
    "image": "/assets/images/DevFest Nairobi 2025.jpeg",
    "description": "Free developer conference by Google Developer Groups",
    "rating": 4.8,
    "reviews_count": 123,
    "days_of_week": ["Saturday"]
  },
  {
    "id": 8,
    "title": "East Africa Business Summit",
    "date": "2025-01-30",
    "start_time": "08:00",
    "end_time": "17:30",
    "location": "Villa Rosa Kempinski, Nairobi",
    "venue_name": "Villa Rosa Kempinski",
    "address": "Chiromo Road, Nairobi, Kenya",
    "category": "Business",
    "theme": "Corporate",
    "ticket_price": 12000,
    "early_bird_price": 9500,
    "max_attendees": 500,
    "tickets_sold": 280,
    "image": "/assets/images/East Africa Business Summit.jpeg",
    "description": "Regional business leaders gathering for networking and insights",
    "rating": 4.6,
    "reviews_count": 67,
    "days_of_week": ["Thursday"]
  },
  {
    "id": 9,
    "title": "Women in Business Kenya Conference",
    "date": "2025-03-08",
    "start_time": "09:00",
    "end_time": "16:00",
    "location": "Radisson Blu Hotel, Nairobi",
    "venue_name": "Radisson Blu Hotel",
    "address": "Upper Hill, Nairobi, Kenya",
    "category": "Business",
    "theme": "Networking",
    "ticket_price": 4500,
    "early_bird_price": 3500,
    "max_attendees": 800,
    "tickets_sold": 450,
    "image": "/assets/images/Women in Business Kenya Conference.jpeg",
    "description": "Empowering women entrepreneurs and business leaders",
    "rating": 4.8,
    "reviews_count": 92,
    "days_of_week": ["Saturday"]
  },
  {
    "id": 10,
    "title": "Nairobi Restaurant Week",
    "date": "2025-02-20",
    "start_time": "12:00",
    "end_time": "22:00",
    "location": "Various Restaurants, Nairobi",
    "venue_name": "Multiple Venues",
    "address": "Nairobi, Kenya",
    "category": "Food",
    "theme": "Festival",
    "ticket_price": 0,
    "max_attendees": 10000,
    "tickets_sold": 3500,
    "image": "/assets/images/Nairobi Restaurant Week.jpeg",
    "description": "Week-long celebration of Nairobi's culinary scene",
    "rating": 4.5,
    "reviews_count": 234,
    "days_of_week": ["Thursday", "Friday", "Saturday", "Sunday"]
  },
  {
    "id": 11,
    "title": "Kenyan Coffee Festival",
    "date": "2025-04-12",
    "start_time": "10:00",
    "end_time": "18:00",
    "location": "Karura Forest, Nairobi",
    "venue_name": "Karura Forest",
    "address": "Limuru Road, Nairobi, Kenya",
    "category": "Food",
    "theme": "Festival",
    "ticket_price": 1500,
    "early_bird_price": 1200,
    "max_attendees": 2000,
    "tickets_sold": 650,
    "image": "/assets/images/Kenyan Coffee Festival.jpeg",
    "description": "Celebrating Kenya's world-renowned coffee culture",
    "rating": 4.7,
    "reviews_count": 89,
    "days_of_week": ["Saturday"]
  },
  {
    "id": 12,
    "title": "Nairobi City Marathon",
    "date": "2025-03-30",
    "start_time": "06:00",
    "end_time": "12:00",
    "location": "Nyayo Stadium, Nairobi",
    "venue_name": "Nyayo Stadium",
    "address": "Uhuru Highway, Nairobi, Kenya",
    "category": "Sports",
    "theme": "Competition",
    "ticket_price": 2500,
    "early_bird_price": 2000,
    "max_attendees": 15000,
    "tickets_sold": 8900,
    "image": "/assets/images/Nairobi City Marathon.jpeg",
    "description": "Annual marathon through the streets of Nairobi",
    "rating": 4.6,
    "reviews_count": 456,
    "days_of_week": ["Sunday"]
  },
  {
    "id": 13,
    "title": "Rhino Charge 2025",
    "date": "2025-06-07",
    "start_time": "07:00",
    "end_time": "17:00",
    "location": "Maasai Mara, Kenya",
    "venue_name": "Maasai Mara National Reserve",
    "address": "Maasai Mara, Kenya",
    "category": "Sports",
    "theme": "Competition",
    "ticket_price": 15000,
    "early_bird_price": 12000,
    "max_attendees": 500,
    "tickets_sold": 320,
    "image": "/assets/images/Rhino Charge 2025.jpeg",
    "description": "Off-road motorsport event supporting rhino conservation",
    "rating": 4.9,
    "reviews_count": 78,
    "days_of_week": ["Saturday"]
  },
  {
    "id": 14,
    "title": "Nairobi Art Fair",
    "date": "2025-05-15",
    "start_time": "10:00",
    "end_time": "19:00",
    "location": "Sarit Centre, Nairobi",
    "venue_name": "Sarit Centre",
    "address": "Westlands, Nairobi, Kenya",
    "category": "Art",
    "theme": "Cultural",
    "ticket_price": 1000,
    "max_attendees": 3000,
    "tickets_sold": 1200,
    "image": "/assets/images/Nairobi Art Fair.jpeg",
    "description": "Contemporary African art exhibition and marketplace",
    "rating": 4.4,
    "reviews_count": 67,
    "days_of_week": ["Thursday", "Friday", "Saturday"]
  },
  {
    "id": 15,
    "title": "Lamu Cultural Festival",
    "date": "2025-08-20",
    "start_time": "09:00",
    "end_time": "22:00",
    "location": "Lamu Old Town, Lamu",
    "venue_name": "Lamu Old Town",
    "address": "Lamu Island, Kenya",
    "category": "Cultural",
    "theme": "Festival",
    "ticket_price": 3500,
    "early_bird_price": 2800,
    "max_attendees": 2000,
    "tickets_sold": 450,
    "image": "/assets/images/Lamu Cultural Festival.jpeg",
    "description": "Celebrating Swahili culture and heritage in historic Lamu",
    "rating": 4.8,
    "reviews_count": 123,
    "days_of_week": ["Saturday", "Sunday"]
  },
  {
    "id": 16,
    "title": "Nairobi Fashion Week",
    "date": "2025-10-18",
    "start_time": "18:00",
    "end_time": "23:00",
    "location": "Sarit Centre, Nairobi",
    "venue_name": "Sarit Centre",
    "address": "Westlands, Nairobi, Kenya",
    "category": "Fashion",
    "theme": "Fashion Show",
    "ticket_price": 5000,
    "early_bird_price": 4000,
    "max_attendees": 1000,
    "tickets_sold": 650,
    "image": "/assets/images/Nairobi Fashion Week.jpeg",
    "description": "Showcasing the best of African fashion and design",
    "rating": 4.7,
    "reviews_count": 89,
    "days_of_week": ["Friday", "Saturday"]
  },
  {
    "id": 17,
    "title": "Churchill Show Live",
    "date": "2024-12-31",
    "start_time": "20:00",
    "end_time": "23:59",
    "location": "KICC, Nairobi",
    "venue_name": "Kenyatta International Convention Centre",
    "address": "Harambee Avenue, Nairobi, Kenya",
    "category": "Entertainment",
    "theme": "Comedy",
    "ticket_price": 3000,
    "early_bird_price": 2500,
    "max_attendees": 5000,
    "tickets_sold": 4200,
    "image": "/assets/images/Churchill Show Live.jpeg",
    "description": "New Year's Eve comedy special with Kenya's top comedians",
    "rating": 4.6,
    "reviews_count": 234,
    "days_of_week": ["Tuesday"]
  },
  {
    "id": 18,
    "title": "Kenya Education Summit",
    "date": "2025-09-12",
    "start_time": "08:00",
    "end_time": "17:00",
    "location": "Kenyatta University, Nairobi",
    "venue_name": "Kenyatta University",
    "address": "Thika Road, Nairobi, Kenya",
    "category": "Education",
    "theme": "Conference",
    "ticket_price": 2500,
    "early_bird_price": 2000,
    "max_attendees": 1500,
    "tickets_sold": 680,
    "image": "/assets/images/Kenya Education Summit.jpeg",
    "description": "Transforming education in Kenya through innovation",
    "rating": 4.5,
    "reviews_count": 56,
    "days_of_week": ["Friday"]
  },
  {
    "id": 19,
    "title": "Nairobi Health & Wellness Expo",
    "date": "2025-07-26",
    "start_time": "09:00",
    "end_time": "17:00",
    "location": "Sarit Centre, Nairobi",
    "venue_name": "Sarit Centre",
    "address": "Westlands, Nairobi, Kenya",
    "category": "Health",
    "theme": "Expo",
    "ticket_price": 500,
    "max_attendees": 5000,
    "tickets_sold": 1800,
    "image": "/assets/images/Nairobi Food & Wine Festival.jpeg",
    "description": "Promoting health and wellness in the community",
    "rating": 4.3,
    "reviews_count": 78,
    "days_of_week": ["Saturday"]
  },
  {
    "id": 20,
    "title": "Afro Fusion Concert - Flash Sale",
    "date": "2025-01-14",
    "start_time": "19:00",
    "end_time": "23:00",
    "location": "Carnivore Grounds, Nairobi",
    "venue_name": "Carnivore Grounds",
    "address": "Langata Road, Nairobi, Kenya",
    "category": "Music",
    "theme": "Concert",
    "ticket_price": 4000,
    "early_bird_price": 2000,
    "flash_sale": True,
    "discount_percentage": 50,
    "max_attendees": 3000,
    "tickets_sold": 2100,
    "image": "/assets/images/Afro Fusion Concert.jpeg",
    "description": "50% OFF Flash Sale! Afro fusion music concert",
    "rating": 4.8,
    "reviews_count": 145,
    "days_of_week": ["Tuesday"]
  }
]
    
    # Empty list to store vendor services (like catering, photography, etc.)
    services_db = []
    # Empty list to store notifications for the app
    notifications_db = []

    # Function to create and send notifications when events are created/updated
    def send_notification(type, data):
        # Add a new notification to the notifications list
        notifications_db.append({
            'id': len(notifications_db) + 1,  # Unique ID for each notification
            'type': type,  # Type like 'event_created', 'event_updated'
            'message': f"Event '{data['title']}' has been {type.replace('_', ' ')}",  # Human readable message
            'timestamp': __import__('datetime').datetime.now().isoformat()  # When it was created
        })
    
    # Route to handle getting all events or creating new events
    @app.route('/events', methods=['GET', 'POST', 'OPTIONS'])
    def handle_events():
        # Log the incoming request for debugging
        logger.info(f"Request to /events: {request.method} from {request.remote_addr}")
        logger.info(f"Headers: {dict(request.headers)}")
        # Handle preflight OPTIONS requests
        if request.method == 'OPTIONS':
            return '', 204

        # Try to use the proper event routes from our routes module if available
        try:
            from eventrift.routes.event_routes import EventListResource
            resource = EventListResource()

            if request.method == 'GET':
                logger.info("Using EventListResource for GET")
                return resource.get()
            elif request.method == 'POST':
                logger.info("Using EventListResource for POST")
                return resource.post()

        except Exception as e:
            logger.error(f"Error using EventListResource: {e}")
            # Fallback to simple implementation if routes module not available
            if request.method == 'GET':
                # Return all events from our in-memory database
                return {'success': True, 'events': events_db}
            
            if request.method == 'POST':
                # Check if user is authenticated (has authorization header)
                auth_header = request.headers.get('Authorization')
                if not auth_header:
                    return {'success': False, 'message': 'Authentication required'}, 401

                # Get the JSON data from the request body
                data = request.get_json()
                # Create a new event object with the provided data
                new_event = {
                    'id': len(events_db) + 1,  # Generate unique ID
                    'title': data.get('title'),
                    'description': data.get('description'),
                    'date': data.get('date'),
                    'time': data.get('time'),
                    'location': data.get('location'),
                    'theme': data.get('theme'),
                    'category': data.get('category'),
                    'dress_code': data.get('dress_code'),
                    'ticket_price': data.get('ticket_price'),
                    'image': data.get('image', 'https://via.placeholder.com/400x300'),  # Default image if none provided
                    'organizer_id': 'organizer@example.com'  # Mock organizer for now
                }
                # Add the new event to our events database
                events_db.append(new_event)
                # Send a notification about the new event
                send_notification('event_created', new_event)

                # Return success response with the created event
                return {'success': True, 'message': 'Event created successfully', 'event': new_event}, 201
    
    # Route to handle individual event operations (get, update, delete)
    @app.route('/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
    def handle_event(event_id):
        # Handle preflight OPTIONS requests
        if request.method == 'OPTIONS':
            return '', 204

        if request.method == 'GET':
            # Find the event with the matching ID
            event = next((e for e in events_db if e['id'] == event_id), None)
            if not event:
                return {'success': False, 'message': 'Event not found'}, 404
            # Return the found event
            return {'success': True, 'event': event}
        
        if request.method == 'PUT':
            # Check if user is authenticated
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return {'success': False, 'message': 'Authentication required'}, 401

            # Find the event to update
            event = next((e for e in events_db if e['id'] == event_id), None)
            if not event:
                return {'success': False, 'message': 'Event not found'}, 404

            # Get the update data from request
            data = request.get_json()
            # Update the event with new data (keep old values if not provided)
            event.update({
                'title': data.get('title', event['title']),
                'description': data.get('description', event['description']),
                'date': data.get('date', event['date']),
                'time': data.get('time', event['time']),
                'location': data.get('location', event['location']),
                'theme': data.get('theme', event['theme']),
                'category': data.get('category', event['category']),
                'dress_code': data.get('dress_code', event['dress_code']),
                'ticket_price': data.get('ticket_price', event['ticket_price'])
            })

            # Send notification about the update
            send_notification('event_updated', event)
            # Return success response
            return {'success': True, 'message': 'Event updated successfully', 'event': event}
    
    # Route for user login - creates JWT token for authentication
    @app.route('/auth/login', methods=['POST', 'OPTIONS'])
    @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
    def login():
        if request.method == 'OPTIONS':
            return '', 204

        try:
            data = request.get_json() or {}
            email = data.get('email', 'user@example.com')
            
            # Fast mock authentication
            username = email.split('@')[0] if '@' in email else email
            display_name = username.replace('.', ' ').replace('_', ' ').title()

            from flask_jwt_extended import create_access_token
            access_token = create_access_token(
                identity=email,
                additional_claims={'role': 'Goer'}
            )

            return {
                'success': True,
                'access_token': access_token,
                'user': {
                    'email': email,
                    'username': username,
                    'name': display_name,
                    'role': 'Goer',
                    'id': hash(email) % 10000
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': 'Login failed. Please check your credentials and try again.'
            }, 401
    
    # Route for user registration - creates new user account
    @app.route('/auth/register', methods=['POST', 'OPTIONS'])
    @app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
    def register():
        if request.method == 'OPTIONS':
            return '', 204

        logger.info("Registration request received")
        try:
            data = request.get_json() or {}
            logger.info(f"Registration data: {data}")

            # Simple mock registration for deployment stability
            email = data.get('email', 'user@example.com')
            password = data.get('password', 'password')
            name = data.get('name') or data.get('username', 'User')
            role = data.get('role', 'Goer')

            username = name.lower().replace(' ', '_')
            display_name = name.title()

            from flask_jwt_extended import create_access_token
            access_token = create_access_token(
                identity=email,
                additional_claims={'role': role}
            )

            logger.info(f"Registration successful for {email}")
            return {
                'success': True,
                'message': 'User registered successfully',
                'access_token': access_token,
                'user': {
                    'id': hash(email) % 10000,
                    'email': email,
                    'username': username,
                    'name': display_name,
                    'role': role
                }
            }, 201

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {
                'success': False,
                'message': 'Registration failed. Please check your information and try again.'
            }, 400
    
    # Route to get current user's profile information
    @app.route('/auth/profile', methods=['GET', 'OPTIONS'])
    def get_profile():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204

        try:
            # Log the profile request
            logger.info(f"Profile request from {request.remote_addr}")
            logger.info(f"Request headers: {dict(request.headers)}")

            # Check for Authorization header with Bearer token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning("Profile failed - no token provided")
                return {'success': False, 'message': 'No token provided'}, 401

            # Mock user profile - in real app this would decode JWT to get actual user
            logger.info("Profile successful")
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
        except Exception as e:
            logger.error(f"Profile error - {str(e)}")
            return {'success': False, 'message': 'Invalid token'}, 401
    
    # Route to handle vendor services (get all or create new)
    @app.route('/services', methods=['GET', 'POST', 'OPTIONS'])
    def handle_services():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204

        if request.method == 'GET':
            # Return all services from our database
            return {'success': True, 'services': services_db}

        if request.method == 'POST':
            # Check if user is authenticated
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return {'success': False, 'message': 'Authentication required'}, 401

            # Get service data from request
            data = request.get_json()
            # Create new service object
            new_service = {
                'id': len(services_db) + 1,  # Generate unique ID
                'name': data.get('name'),
                'description': data.get('description'),
                'price': data.get('price'),
                'category': data.get('category'),
                'vendor_id': 'vendor@example.com'  # Mock vendor for now
            }
            # Add service to database
            services_db.append(new_service)

            # Return success response
            return {'success': True, 'message': 'Service created successfully', 'service': new_service}, 201
    
    # Route to handle individual service operations (get, update, delete)
    @app.route('/services/<int:service_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
    def handle_service(service_id):
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204

        if request.method == 'PUT':
            # Check authentication
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return {'success': False, 'message': 'Authentication required'}, 401

            # Find the service to update
            service = next((s for s in services_db if s['id'] == service_id), None)
            if not service:
                return {'success': False, 'message': 'Service not found'}, 404

            # Get update data and apply changes
            data = request.get_json()
            service.update({
                'name': data.get('name', service['name']),
                'description': data.get('description', service['description']),
                'price': data.get('price', service['price']),
                'category': data.get('category', service['category'])
            })

            # Return success response
            return {'success': True, 'message': 'Service updated successfully', 'service': service}
    
    # Route to get all notifications for the app
    @app.route('/notifications', methods=['GET', 'OPTIONS'])
    def get_notifications():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204
        # Return all notifications from our database
        return {'success': True, 'notifications': notifications_db}
    
    # Route to get dashboard data for event organizers
    @app.route('/dashboard/organizer', methods=['GET', 'OPTIONS'])
    def organizer_dashboard():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204

        # Check if user is authenticated
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return {'success': False, 'message': 'Authentication required'}, 401

        # Get all events created by this organizer
        organizer_events = [e for e in events_db if e.get('organizer_id') == 'organizer@example.com']

        # Calculate additional metrics for dashboard
        total_tickets_sold = sum(event.get('tickets_sold', 0) for event in organizer_events)
        total_revenue = sum(event.get('tickets_sold', 0) * event.get('ticket_price', 0) for event in organizer_events)
        upcoming_events = []
        past_events = []

        from datetime import datetime
        current_date = datetime.now()

        for event in organizer_events:
            event_date = datetime.fromisoformat(event['date'])
            if event_date >= current_date:
                upcoming_events.append(event)
            else:
                past_events.append(event)

        # Return comprehensive dashboard data
        return {
            'success': True,
            'events': organizer_events,
            'total_events': len(organizer_events),
            'upcoming_events': len(upcoming_events),
            'past_events': len(past_events),
            'total_tickets_sold': total_tickets_sold,
            'total_revenue': total_revenue,
            'recent_events': sorted(organizer_events, key=lambda x: x['date'], reverse=True)[:5]  # Last 5 events
        }
    
    # Route to get dashboard data for vendors (service providers)
    @app.route('/dashboard/vendor', methods=['GET', 'OPTIONS'])
    def vendor_dashboard():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204

        # Check if user is authenticated
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return {'success': False, 'message': 'Authentication required'}, 401

        # Get all services offered by this vendor
        vendor_services = [s for s in services_db if s.get('vendor_id') == 'vendor@example.com']

        # Calculate additional metrics for vendor dashboard
        total_bookings = sum(len([b for b in ticket_bookings_db if any(s['id'] == b.get('service_id') for s in vendor_services)]) for s in vendor_services)
        total_revenue = sum(service.get('price', 0) for service in vendor_services)

        # Group services by category
        services_by_category = {}
        for service in vendor_services:
            category = service.get('category', 'Other')
            if category not in services_by_category:
                services_by_category[category] = []
            services_by_category[category].append(service)

        # Return comprehensive vendor dashboard data
        return {
            'success': True,
            'services': vendor_services,
            'total_services': len(vendor_services),
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'services_by_category': services_by_category,
            'categories_count': len(services_by_category),
            'recent_services': sorted(vendor_services, key=lambda x: x.get('id', 0), reverse=True)[:5]  # Last 5 services
        }

    # Route to get all events for a specific organizer
    @app.route('/organizers/events', methods=['GET', 'OPTIONS'])
    def get_organizer_events():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204

        # Check authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return {'success': False, 'message': 'Authentication required'}, 401

        # Get all events created by this organizer
        organizer_events = [e for e in events_db if e.get('organizer_id') == 'organizer@example.com']
        # Return the events
        return {
            'success': True,
            'events': organizer_events
        }


    # Simple route to check if server is running
    @app.route('/')
    def hello():
        return {'message': 'EventRift Server is running!'}

    # Health check route for monitoring
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'message': 'EventRift API is running'}
    
    # API prefix routes are now handled by the main auth routes above
    
    # Test route to verify CORS configuration is working
    @app.route('/test', methods=['GET', 'OPTIONS'])
    def test_cors():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204
        # Return test data showing CORS configuration
        return {
            'success': True,
            'message': 'CORS is working!',
            'frontend_url': 'https://event-rift-client.vercel.app',
            'backend_url': request.url_root,
            'allowed_origins': [
                'http://localhost:3000',
                'http://localhost:5173',
                'http://localhost:5174',
                'https://*.vercel.app',
                'https://event-rift-client.vercel.app'
            ]
        }
    
    # API prefix routes - these call the same functions as the non-API routes
    # but have /api/ prefix for frontend compatibility
    @app.route('/api/events', methods=['GET', 'POST', 'OPTIONS'])
    def api_events():
        # Use fallback implementation to avoid database connection issues
        return handle_events()

    @app.route('/api/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
    def api_event(event_id):
        # Use fallback implementation to avoid database connection issues
        return handle_event(event_id)

    @app.route('/services', methods=['GET', 'POST', 'OPTIONS'])
    @app.route('/api/services', methods=['GET', 'POST', 'OPTIONS'])
    def api_services():
        # Try to use proper vendor service routes if available
        try:
            from eventrift.routes.vendor_routes import VendorServiceListResource
            resource = VendorServiceListResource()
            if request.method == 'GET':
                return resource.get()
            elif request.method == 'POST':
                return resource.post()
        except Exception as e:
            logger.error(f"Error using VendorServiceListResource: {e}")
            return handle_services()

    @app.route('/api/services/<int:service_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
    def api_service(service_id):
        return handle_service(service_id)

    @app.route('/api/notifications', methods=['GET', 'OPTIONS'])
    def api_notifications():
        return get_notifications()

    @app.route('/dashboard/organizer', methods=['GET', 'OPTIONS'])
    @app.route('/api/dashboard/organizer', methods=['GET', 'OPTIONS'])
    def api_organizer_dashboard():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204

        try:
            # Check if user is authenticated
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'success': False, 'message': 'Authentication required'}, 401

            # Try to use proper dashboard routes if available
            try:
                from eventrift.routes.dashboard_routes import get_organizer_dashboard
                return get_organizer_dashboard(1)  # Mock user ID
            except ImportError:
                pass

            # Get all events created by this organizer (mock data for now)
            organizer_events = [e for e in events_db if e.get('organizer_id') == 'organizer@example.com']

            # Calculate comprehensive metrics
            total_events = len(organizer_events)
            total_tickets_sold = sum(event.get('tickets_sold', 0) for event in organizer_events)
            total_revenue = sum(event.get('tickets_sold', 0) * event.get('ticket_price', 0) for event in organizer_events)

            # Separate upcoming and past events
            upcoming_events = []
            past_events = []
            from datetime import datetime
            current_date = datetime.now()

            for event in organizer_events:
                try:
                    event_date = datetime.fromisoformat(event['date'])
                    if event_date >= current_date:
                        upcoming_events.append(event)
                    else:
                        past_events.append(event)
                except (ValueError, KeyError):
                    # If date parsing fails, consider it upcoming
                    upcoming_events.append(event)

            # Get recent events (last 5 by date)
            recent_events = sorted(organizer_events, key=lambda x: x.get('date', ''), reverse=True)[:5]

            # Calculate attendance rate (mock data)
            avg_attendance_rate = 85.5  # Mock percentage

            # Popular event categories
            categories = {}
            for event in organizer_events:
                category = event.get('category', 'Other')
                categories[category] = categories.get(category, 0) + 1

            top_category = max(categories.items(), key=lambda x: x[1])[0] if categories else 'None'

            return {
                'success': True,
                'events': organizer_events,
                'total_events': total_events,
                'upcoming_events': len(upcoming_events),
                'past_events': len(past_events),
                'total_tickets_sold': total_tickets_sold,
                'total_revenue': total_revenue,
                'avg_attendance_rate': avg_attendance_rate,
                'top_category': top_category,
                'recent_events': recent_events,
                'upcoming_events_list': upcoming_events[:3],  # Next 3 upcoming events
                'monthly_stats': {
                    'this_month_events': len([e for e in organizer_events if e.get('date', '').startswith('2025-11')]),
                    'this_month_revenue': sum(e.get('tickets_sold', 0) * e.get('ticket_price', 0) for e in organizer_events if e.get('date', '').startswith('2025-11')),
                    'this_month_tickets': sum(e.get('tickets_sold', 0) for e in organizer_events if e.get('date', '').startswith('2025-11'))
                }
            }, 200

        except Exception as e:
            logger.error(f"Organizer dashboard error - {str(e)}")
            return {'success': False, 'message': 'Failed to load organizer dashboard'}, 500

    @app.route('/api/dashboard/goer', methods=['GET', 'OPTIONS'])
    def api_goer_dashboard():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204

        try:
            # Check if user is authenticated
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'success': False, 'message': 'Authentication required'}, 401

            # In a real app, decode JWT to get user email. For now, use test@example.com
            user_email = 'test@example.com'

            # Get user's upcoming events (booked tickets for future events)
            user_bookings = [b for b in ticket_bookings_db if b['user_email'] == user_email]

            upcoming_events = []
            past_events = []
            from datetime import datetime
            current_date = datetime.now()

            for booking in user_bookings:
                event = next((e for e in events_db if e['id'] == booking['event_id']), None)
                if event:
                    event_date = datetime.fromisoformat(event['date'])
                    event_data = {
                        'booking_id': booking['id'],
                        'event_id': booking['event_id'],
                        'event_title': event['title'],
                        'event_date': event['date'],
                        'start_time': event['start_time'],
                        'end_time': event['end_time'],
                        'location': event['location'],
                        'venue_name': event['venue_name'],
                        'image': event['image'],
                        'quantity': booking['quantity'],
                        'total_price': booking['total_price'],
                        'status': booking['status'],
                        'booking_date': booking['booking_date']
                    }

                    if event_date >= current_date:
                        upcoming_events.append(event_data)
                    else:
                        past_events.append(event_data)

            # Get user's total spending and booking history
            total_spent = sum(booking['total_price'] for booking in user_bookings)
            total_tickets = sum(booking['quantity'] for booking in user_bookings)

            # Get favorite categories based on bookings
            booked_categories = []
            for booking in user_bookings:
                event = next((e for e in events_db if e['id'] == booking['event_id']), None)
                if event:
                    booked_categories.append(event.get('category', 'Other'))

            from collections import Counter
            favorite_category = Counter(booked_categories).most_common(1)[0][0] if booked_categories else 'None'

            # Get available events for booking (future events)
            available_events = []
            for event in events_db:
                try:
                    event_date = datetime.fromisoformat(event['date'])
                    if event_date >= current_date:
                        available_events.append({
                            'id': event['id'],
                            'title': event['title'],
                            'date': event['date'],
                            'start_time': event['start_time'],
                            'end_time': event['end_time'],
                            'location': event['location'],
                            'venue_name': event['venue_name'],
                            'category': event['category'],
                            'ticket_price': event['ticket_price'],
                            'max_attendees': event['max_attendees'],
                            'tickets_sold': event['tickets_sold'],
                            'image': event['image'],
                            'description': event['description'],
                            'rating': event['rating']
                        })
                except (ValueError, KeyError):
                    continue

            return {
                'success': True,
                'user': {
                    'email': user_email,
                    'total_spent': total_spent,
                    'total_tickets': total_tickets,
                    'favorite_category': favorite_category
                },
                'upcoming_events': upcoming_events,
                'past_events': past_events,
                'available_events': available_events,
                'stats': {
                    'total_upcoming_events': len(upcoming_events),
                    'total_past_events': len(past_events),
                    'total_bookings': len(user_bookings),
                    'total_spent': total_spent,
                    'total_tickets': total_tickets
                },
                'recent_bookings': sorted(user_bookings, key=lambda x: x['booking_date'], reverse=True)[:5]
            }, 200

        except Exception as e:
            logger.error(f"Goer dashboard error - {str(e)}")
            return {'success': False, 'message': 'Failed to load dashboard'}, 500

    @app.route('/dashboard/vendor', methods=['GET', 'OPTIONS'])
    @app.route('/api/dashboard/vendor', methods=['GET', 'OPTIONS'])
    def api_vendor_dashboard():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204

        try:
            # Check if user is authenticated
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'success': False, 'message': 'Authentication required'}, 401

            # Try to use proper dashboard routes if available
            try:
                from eventrift.routes.dashboard_routes import get_vendor_dashboard
                return get_vendor_dashboard(1)  # Mock user ID
            except ImportError:
                pass

            # Get all services offered by this vendor
            vendor_services = [s for s in services_db if s.get('vendor_id') == 'vendor@example.com']

            # Calculate comprehensive metrics
            total_services = len(vendor_services)
            total_revenue = sum(service.get('price', 0) for service in vendor_services)

            # Calculate total bookings (mock data - in real app this would be from booking records)
            total_bookings = sum(len([b for b in ticket_bookings_db if any(s['id'] == b.get('service_id') for s in vendor_services)]) for s in vendor_services)

            # Group services by category with counts and revenue
            services_by_category = {}
            category_revenue = {}
            category_bookings = {}

            for service in vendor_services:
                category = service.get('category', 'Other')

                if category not in services_by_category:
                    services_by_category[category] = []
                    category_revenue[category] = 0
                    category_bookings[category] = 0

                services_by_category[category].append(service)
                category_revenue[category] += service.get('price', 0)
                # Mock booking calculation per service
                category_bookings[category] += len([b for b in ticket_bookings_db if b.get('service_id') == service.get('id')])

            # Calculate average service price
            avg_service_price = total_revenue / total_services if total_services > 0 else 0

            # Get most popular category
            most_popular_category = max(category_bookings.items(), key=lambda x: x[1])[0] if category_bookings else 'None'

            # Get recent services (last 5 by ID)
            recent_services = sorted(vendor_services, key=lambda x: x.get('id', 0), reverse=True)[:5]

            # Calculate monthly stats (mock data)
            monthly_revenue = sum(s.get('price', 0) for s in vendor_services) * 0.3  # Mock 30% monthly
            monthly_bookings = int(total_bookings * 0.4)  # Mock 40% monthly

            return {
                'success': True,
                'services': vendor_services,
                'total_services': total_services,
                'total_bookings': total_bookings,
                'total_revenue': total_revenue,
                'avg_service_price': avg_service_price,
                'services_by_category': services_by_category,
                'categories_count': len(services_by_category),
                'category_revenue': category_revenue,
                'category_bookings': category_bookings,
                'most_popular_category': most_popular_category,
                'recent_services': recent_services,
                'monthly_stats': {
                    'this_month_revenue': monthly_revenue,
                    'this_month_bookings': monthly_bookings,
                    'this_month_services': len([s for s in vendor_services if s.get('id', 0) > 5])  # Mock recent services
                },
                'performance_metrics': {
                    'customer_satisfaction': 4.6,  # Mock rating
                    'response_time': '2.3 hours',  # Mock response time
                    'completion_rate': 94.2  # Mock completion percentage
                }
            }, 200

        except Exception as e:
            logger.error(f"Vendor dashboard error - {str(e)}")
            return {'success': False, 'message': 'Failed to load vendor dashboard'}, 500
    
    @app.route('/api/health', methods=['GET', 'OPTIONS'])
    def api_health():
        return health()
    
    @app.route('/api/test', methods=['GET', 'OPTIONS'])
    def api_test():
        return test_cors()
    
    # API route for user logout
    @app.route('/api/auth/logout', methods=['POST', 'OPTIONS'])
    def api_logout():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204

        try:
            # Log the logout request
            logger.info(f"API logout request from {request.remote_addr}")
            logger.info(f"Request headers: {dict(request.headers)}")

            # Check for Authorization header (optional for logout)
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                logger.info("API logout with valid token")
            else:
                logger.info("API logout without token")

            logger.info("API logout successful")
            # Return success response
            return {
                'success': True,
                'message': 'Logged out successfully'
            }
        except Exception as e:
            logger.error(f"API logout error - {str(e)}")
            return {'success': False, 'message': 'Logout failed'}, 500

    # API route to get current user's profile with /api/ prefix
    @app.route('/api/auth/profile', methods=['GET', 'OPTIONS'])
    def api_get_profile():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204

        try:
            # Log the profile request
            logger.info(f"API profile request from {request.remote_addr}")
            logger.info(f"Request headers: {dict(request.headers)}")

            # Check for Authorization header with Bearer token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning("API profile failed - no token provided")
                return {'success': False, 'message': 'No token provided'}, 401

            # Mock user profile - in real app this would decode JWT to get actual user data
            logger.info("API profile successful")
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
        except Exception as e:
            logger.error(f"API profile error - {str(e)}")
            return {'success': False, 'message': 'Invalid token'}, 401

    # Ticket booking functionality - store user's event ticket purchases
    ticket_bookings_db = []

    # Route for users to book tickets for events
    @app.route('/api/tickets/book', methods=['POST', 'OPTIONS'])
    def book_ticket():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204

        try:
            # Log the booking request
            logger.info("🎫 TICKET BOOKING REQUEST RECEIVED")
            logger.info(f"Request headers: {dict(request.headers)}")

            # Check for Authorization header with Bearer token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning("❌ Ticket booking failed - no token provided")
                return {'success': False, 'message': 'Authentication required'}, 401

            # Get booking data from request
            data = request.get_json()
            logger.info(f"📋 Booking data received: {data}")

            event_id = data.get('event_id')
            quantity = data.get('quantity', 1)  # Default to 1 ticket if not specified
            user_email = data.get('user_email', 'test@example.com')  # In real app, this comes from JWT token

            # Validate that event_id is provided
            if not event_id:
                logger.warning("❌ Event ID is required")
                return {'success': False, 'message': 'Event ID is required'}, 400

            # Find the event in our database
            event = next((e for e in events_db if e['id'] == event_id), None)
            if not event:
                logger.warning(f"❌ Event not found: {event_id}")
                return {'success': False, 'message': 'Event not found'}, 404

            # Check if enough tickets are available
            tickets_available = event['max_attendees'] - event['tickets_sold']
            if quantity > tickets_available:
                logger.warning(f"❌ Not enough tickets available. Requested: {quantity}, Available: {tickets_available}")
                return {'success': False, 'message': f'Only {tickets_available} tickets available'}, 400

            # Calculate total cost for the tickets
            total_price = event['ticket_price'] * quantity

            # Create booking record
            booking = {
                'id': len(ticket_bookings_db) + 1,  # Generate unique booking ID
                'event_id': event_id,
                'user_email': user_email,
                'quantity': quantity,
                'total_price': total_price,
                'status': 'CONFIRMED',  # Mark as confirmed
                'booking_date': __import__('datetime').datetime.now().isoformat(),  # Current timestamp
                'event_title': event['title']  # Store event title for easy reference
            }

            # Add booking to our database
            ticket_bookings_db.append(booking)

            # Update event tickets sold
            event['tickets_sold'] += quantity

            # Console logging for successful booking
            print("🎉" + "="*60)
            print("🎫 TICKET BOOKING SUCCESSFUL!")
            print(f"👤 User: {user_email}")
            print(f"🎪 Event: {event['title']} (ID: {event_id})")
            print(f"🎯 Quantity: {quantity} ticket(s)")
            print(f"💰 Total Price: KES {total_price:,}")
            print(f"📅 Event Date: {event['date']}")
            print(f"📍 Venue: {event['venue_name']}")
            print(f"🆔 Booking ID: {booking['id']}")
            print(f"📊 Tickets remaining: {event['max_attendees'] - event['tickets_sold']}")
            print("🎉" + "="*60)

            logger.info(f"✅ Ticket booking successful: {booking}")

            # Return success response with booking details
            return {
                'success': True,
                'message': f'🎉 Successfully booked {quantity} ticket(s) for {event["title"]}!',
                'booking': booking,
                'event': {
                    'title': event['title'],
                    'date': event['date'],
                    'venue': event['venue_name'],
                    'tickets_remaining': event['max_attendees'] - event['tickets_sold']
                }
            }, 201

        except Exception as e:
            logger.error(f"❌ Ticket booking error - {str(e)}")
            print(f"💥 BOOKING ERROR: {str(e)}")
            return {'success': False, 'message': 'Booking failed'}, 500

    # Route to get all tickets booked by the current user
    @app.route('/tickets/user', methods=['GET', 'OPTIONS'])
    @app.route('/api/tickets/user', methods=['GET', 'OPTIONS'])
    def get_user_tickets():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204

        try:
            # Log the request
            logger.info("User tickets request received")
            logger.info(f"Request headers: {dict(request.headers)}")

            # Check for Authorization header with Bearer token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning("User tickets failed - no token provided")
                return {'success': False, 'message': 'Authentication required'}, 401

            # In a real app, you'd decode the JWT to get the actual user email
            # For now, return mock bookings for test@example.com
            user_bookings = [b for b in ticket_bookings_db if b['user_email'] == 'test@example.com']

            # Create enhanced list of upcoming events with full event details
            upcoming_events = []
            for booking in user_bookings:
                # Find the full event details for this booking
                event = next((e for e in events_db if e['id'] == booking['event_id']), None)
                if event:
                    # Check if the event is in the future (upcoming)
                    from datetime import datetime
                    event_date = datetime.fromisoformat(event['date'])
                    current_date = datetime.now()

                    # Only include events that haven't happened yet
                    if event_date >= current_date:
                        upcoming_events.append({
                            'booking_id': booking['id'],
                            'event_id': booking['event_id'],
                            'event_title': event['title'],
                            'event_date': event['date'],
                            'start_time': event['start_time'],
                            'end_time': event['end_time'],
                            'location': event['location'],
                            'venue_name': event['venue_name'],
                            'image': event['image'],
                            'quantity': booking['quantity'],
                            'total_price': booking['total_price'],
                            'status': booking['status'],
                            'booking_date': booking['booking_date']
                        })

            logger.info(f"User tickets retrieved: {len(user_bookings)} total bookings, {len(upcoming_events)} upcoming events")

            # Return both all bookings and filtered upcoming events
            return {
                'success': True,
                'tickets': user_bookings,
                'upcoming_events': upcoming_events
            }, 200

        except Exception as e:
            logger.error(f"User tickets error - {str(e)}")
            return {'success': False, 'message': 'Failed to retrieve tickets'}, 500

    # Debug route to show all available API endpoints and data counts
    @app.route('/api/debug', methods=['GET', 'OPTIONS'])
    def api_debug():
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return '', 204

        # Collect all API endpoints from the app's URL map
        all_endpoints = []
        for rule in app.url_map.iter_rules():
            # Only include routes that start with /api
            if rule.rule.startswith('/api'):
                # Get HTTP methods for this route, excluding HEAD and OPTIONS
                methods = [method for method in rule.methods if method not in ['HEAD', 'OPTIONS']]
                all_endpoints.append(f"{'/'.join(methods)} {rule.rule}")

        # Return debug information
        return {
            'success': True,
            'endpoints': sorted(all_endpoints),  # Sort endpoints alphabetically
            'data_counts': {
                'events': len(events_db),
                'services': len(services_db),
                'notifications': len(notifications_db),
                'ticket_bookings': len(ticket_bookings_db)
            }
        }
    
    # Error handler for 404 Not Found errors
    @app.errorhandler(404)
    def not_found(error):
        return {'success': False, 'error': 'Endpoint not found'}, 404

    # Error handler for 500 Internal Server Error
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {'success': False, 'error': 'Internal server error', 'message': 'Something went wrong on the server'}, 500
    
    # Error handler for 400 Bad Request
    @app.errorhandler(400)
    def bad_request(error):
        return {'success': False, 'error': 'Bad request', 'message': 'Invalid request data'}, 400
    
    # Global exception handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}")
        return {'success': False, 'error': 'Server error', 'message': 'An unexpected error occurred'}, 500

    # Return the configured Flask app
    return app

# Create the Flask application instance
app = create_app()

# Run the app if this file is executed directly (not imported)
if __name__ == '__main__':
    app.run(port=5555, debug=True)