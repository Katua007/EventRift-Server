from flask import Flask, request
from flask_cors import CORS
import os
import sys
import logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from eventrift.config import Config
    from eventrift.extensions import db, migrate, api, jwt
except ImportError:
    # Fallback for basic Flask app
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate
    from flask_restful import Api
    from flask_jwt_extended import JWTManager
    
    class Config:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///eventrift.db')
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-secret')
        SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')
    
    db = SQLAlchemy()
    migrate = Migrate()
    api = Api()
    jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for frontend integration
    # Allow multiple origins for development and production
    allowed_origins = [
        'http://localhost:3000',      # React dev server
        'http://localhost:5173',      # Vite dev server
        'http://localhost:5174',      # Alternative Vite port
        'https://*.vercel.app',       # Vercel deployments
        'https://event-rift-client.vercel.app',  # Production frontend
    ]

    # Get frontend URL from environment or use default
    frontend_url = os.environ.get('FRONTEND_URL', 'https://event-rift-client.vercel.app')
    if frontend_url not in allowed_origins:
        allowed_origins.append(frontend_url)

    # Configure CORS with proper preflight handling
    CORS(app,
          origins=allowed_origins,
          methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
          allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
          supports_credentials=True,
          expose_headers=['Content-Type', 'Authorization'])
    
    # Add explicit OPTIONS handler for all routes
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            origin = request.headers.get('Origin')
            logger.info(f"OPTIONS preflight request received for {request.url} from origin: {origin}")
            logger.info(f"Request headers: {dict(request.headers)}")

            response = app.make_default_options_response()
            headers = response.headers

            # Check if origin is allowed
            if origin in allowed_origins or origin in ['https://*.vercel.app', 'http://localhost:3000', 'http://localhost:5173', 'http://localhost:5174']:
                headers['Access-Control-Allow-Origin'] = origin
            else:
                headers['Access-Control-Allow-Origin'] = frontend_url

            headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept'
            headers['Access-Control-Allow-Credentials'] = 'true'
            logger.info(f"CORS headers set: {headers}")
            return response, 204

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    jwt.init_app(app)

    # Initialize routes
    try:
        from eventrift.routes import initialize_routes
        initialize_routes(app)
    except ImportError:
        pass

    # Global storage - Events from frontend data
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
    
    services_db = []
    notifications_db = []
    
    def send_notification(type, data):
        notifications_db.append({
            'id': len(notifications_db) + 1,
            'type': type,
            'message': f"Event '{data['title']}' has been {type.replace('_', ' ')}",
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
    
    @app.route('/events', methods=['GET', 'POST', 'OPTIONS'])
    def handle_events():
        logger.info(f"Request to /events: {request.method} from {request.remote_addr}")
        logger.info(f"Headers: {dict(request.headers)}")
        if request.method == 'OPTIONS':
            return '', 204

        # Try to use the proper event routes if available
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
            # Fallback to simple implementation
            if request.method == 'GET':
                return {'success': True, 'events': events_db}
            
            if request.method == 'POST':
                auth_header = request.headers.get('Authorization')
                if not auth_header:
                    return {'success': False, 'message': 'Authentication required'}, 401
                
                data = request.get_json()
                new_event = {
                    'id': len(events_db) + 1,
                    'title': data.get('title'),
                    'description': data.get('description'),
                    'date': data.get('date'),
                    'time': data.get('time'),
                    'location': data.get('location'),
                    'theme': data.get('theme'),
                    'category': data.get('category'),
                    'dress_code': data.get('dress_code'),
                    'ticket_price': data.get('ticket_price'),
                    'image': data.get('image', 'https://via.placeholder.com/400x300'),
                    'organizer_id': 'organizer@example.com'
                }
                events_db.append(new_event)
                send_notification('event_created', new_event)
                
                return {'success': True, 'message': 'Event created successfully', 'event': new_event}, 201
    
    @app.route('/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
    def handle_event(event_id):
        if request.method == 'OPTIONS':
            return '', 204
        
        if request.method == 'GET':
            event = next((e for e in events_db if e['id'] == event_id), None)
            if not event:
                return {'success': False, 'message': 'Event not found'}, 404
            return {'success': True, 'event': event}
        
        if request.method == 'PUT':
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return {'success': False, 'message': 'Authentication required'}, 401
            
            event = next((e for e in events_db if e['id'] == event_id), None)
            if not event:
                return {'success': False, 'message': 'Event not found'}, 404
            
            data = request.get_json()
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
            
            send_notification('event_updated', event)
            return {'success': True, 'message': 'Event updated successfully', 'event': event}
    
    @app.route('/auth/login', methods=['POST', 'OPTIONS'])
    def login():
        logger.info(f"Login request from {request.remote_addr}")
        logger.info(f"Request headers: {dict(request.headers)}")
        if request.method == 'OPTIONS':
            return '', 204

        data = request.get_json()
        logger.info(f"Login data received: {data}")
        email = data.get('email')
        password = data.get('password')

        if email and password:
            from flask_jwt_extended import create_access_token
            access_token = create_access_token(identity=email)
            logger.info(f"Login successful for {email}")
            return {
                'success': True,
                'access_token': access_token,
                'user': {
                    'email': email,
                    'username': email.split('@')[0] if '@' in email else email,
                    'name': email.split('@')[0] if '@' in email else email,
                    'role': 'user'
                }
            }
        logger.warning(f"Login failed - missing credentials")
        return {'success': False, 'message': 'Invalid credentials'}, 401
    
    @app.route('/auth/register', methods=['POST', 'OPTIONS'])
    def register():
        if request.method == 'OPTIONS':
            return '', 204
            
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name') or data.get('username')

        if email and password and name:
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': {
                    'email': email,
                    'username': name,
                    'name': name,
                    'role': 'user'
                }
            }, 201
        return {'success': False, 'message': 'Missing required fields'}, 400
    
    @app.route('/auth/profile', methods=['GET', 'OPTIONS'])
    def get_profile():
        if request.method == 'OPTIONS':
            return '', 204

        try:
            logger.info(f"Profile request from {request.remote_addr}")
            logger.info(f"Request headers: {dict(request.headers)}")

            # Check for Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning("Profile failed - no token provided")
                return {'success': False, 'message': 'No token provided'}, 401

            # Mock user profile - in real app this would decode JWT
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
    
    @app.route('/services', methods=['GET', 'POST', 'OPTIONS'])
    def handle_services():
        if request.method == 'OPTIONS':
            return '', 204
        
        if request.method == 'GET':
            return {'success': True, 'services': services_db}
        
        if request.method == 'POST':
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return {'success': False, 'message': 'Authentication required'}, 401
            
            data = request.get_json()
            new_service = {
                'id': len(services_db) + 1,
                'name': data.get('name'),
                'description': data.get('description'),
                'price': data.get('price'),
                'category': data.get('category'),
                'vendor_id': 'vendor@example.com'
            }
            services_db.append(new_service)
            
            return {'success': True, 'message': 'Service created successfully', 'service': new_service}, 201
    
    @app.route('/services/<int:service_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
    def handle_service(service_id):
        if request.method == 'OPTIONS':
            return '', 204
        
        if request.method == 'PUT':
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return {'success': False, 'message': 'Authentication required'}, 401
            
            service = next((s for s in services_db if s['id'] == service_id), None)
            if not service:
                return {'success': False, 'message': 'Service not found'}, 404
            
            data = request.get_json()
            service.update({
                'name': data.get('name', service['name']),
                'description': data.get('description', service['description']),
                'price': data.get('price', service['price']),
                'category': data.get('category', service['category'])
            })
            
            return {'success': True, 'message': 'Service updated successfully', 'service': service}
    
    @app.route('/notifications', methods=['GET', 'OPTIONS'])
    def get_notifications():
        if request.method == 'OPTIONS':
            return '', 204
        return {'success': True, 'notifications': notifications_db}
    
    @app.route('/dashboard/organizer', methods=['GET', 'OPTIONS'])
    def organizer_dashboard():
        if request.method == 'OPTIONS':
            return '', 204
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return {'success': False, 'message': 'Authentication required'}, 401
        
        organizer_events = [e for e in events_db if e.get('organizer_id') == 'organizer@example.com']
        return {
            'success': True,
            'events': organizer_events,
            'total_events': len(organizer_events)
        }
    
    @app.route('/dashboard/vendor', methods=['GET', 'OPTIONS'])
    def vendor_dashboard():
        if request.method == 'OPTIONS':
            return '', 204

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return {'success': False, 'message': 'Authentication required'}, 401

        vendor_services = [s for s in services_db if s.get('vendor_id') == 'vendor@example.com']
        return {
            'success': True,
            'services': vendor_services,
            'total_services': len(vendor_services)
        }

    @app.route('/organizers/events', methods=['GET', 'OPTIONS'])
    def get_organizer_events():
        if request.method == 'OPTIONS':
            return '', 204

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return {'success': False, 'message': 'Authentication required'}, 401

        organizer_events = [e for e in events_db if e.get('organizer_id') == 'organizer@example.com']
        return {
            'success': True,
            'events': organizer_events
        }


    @app.route('/')
    def hello():
        return {'message': 'EventRift Server is running!'}
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'message': 'EventRift API is running'}
    
    # Add missing routes that should work
    @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
    def api_login():
        logger.info(f"API login request from {request.remote_addr}")
        logger.info(f"Request headers: {dict(request.headers)}")
        if request.method == 'OPTIONS':
            return '', 204

        data = request.get_json()
        logger.info(f"API login data: {data}")
        email = data.get('email') or data.get('email_or_username')
        password = data.get('password')

        if email and password:
            from flask_jwt_extended import create_access_token
            access_token = create_access_token(identity=email)
            logger.info(f"API login successful for {email}")
            return {
                'success': True,
                'access_token': access_token,
                'user': {
                    'email': email,
                    'username': email.split('@')[0] if '@' in email else email,
                    'name': email.split('@')[0] if '@' in email else email,
                    'role': 'user'
                }
            }
        logger.warning(f"API login failed - missing credentials")
        return {'success': False, 'message': 'Invalid credentials'}, 401
    
    @app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
    def api_register():
        if request.method == 'OPTIONS':
            return '', 204
            
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name') or data.get('username')

        if email and password and name:
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': {
                    'email': email,
                    'username': name,
                    'name': name,
                    'role': 'user'
                }
            }, 201
        return {'success': False, 'message': 'Missing required fields'}, 400
    
    @app.route('/test', methods=['GET', 'OPTIONS'])
    def test_cors():
        if request.method == 'OPTIONS':
            return '', 204
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
    
    # Add API prefix routes
    @app.route('/api/events', methods=['GET', 'POST', 'OPTIONS'])
    def api_events():
        # Always use fallback implementation to avoid database issues
        return handle_events()
    
    @app.route('/api/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
    def api_event(event_id):
        # Always use fallback implementation to avoid database issues
        return handle_event(event_id)
    
    @app.route('/api/services', methods=['GET', 'POST', 'OPTIONS'])
    def api_services():
        return handle_services()
    
    @app.route('/api/services/<int:service_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
    def api_service(service_id):
        return handle_service(service_id)
    
    @app.route('/api/notifications', methods=['GET', 'OPTIONS'])
    def api_notifications():
        return get_notifications()
    
    @app.route('/api/dashboard/organizer', methods=['GET', 'OPTIONS'])
    def api_organizer_dashboard():
        return organizer_dashboard()
    
    @app.route('/api/dashboard/vendor', methods=['GET', 'OPTIONS'])
    def api_vendor_dashboard():
        return vendor_dashboard()
    
    @app.route('/api/health', methods=['GET', 'OPTIONS'])
    def api_health():
        return health()
    
    @app.route('/api/test', methods=['GET', 'OPTIONS'])
    def api_test():
        return test_cors()
    
    @app.route('/api/auth/logout', methods=['POST', 'OPTIONS'])
    def api_logout():
        if request.method == 'OPTIONS':
            return '', 204

        try:
            logger.info(f"API logout request from {request.remote_addr}")
            logger.info(f"Request headers: {dict(request.headers)}")

            # Check for Authorization header (optional for logout)
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                logger.info("API logout with valid token")
            else:
                logger.info("API logout without token")

            logger.info("API logout successful")
            return {
                'success': True,
                'message': 'Logged out successfully'
            }
        except Exception as e:
            logger.error(f"API logout error - {str(e)}")
            return {'success': False, 'message': 'Logout failed'}, 500

    @app.route('/api/auth/profile', methods=['GET', 'OPTIONS'])
    def api_get_profile():
        if request.method == 'OPTIONS':
            return '', 204

        try:
            logger.info(f"API profile request from {request.remote_addr}")
            logger.info(f"Request headers: {dict(request.headers)}")

            # Check for Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning("API profile failed - no token provided")
                return {'success': False, 'message': 'No token provided'}, 401

            # Mock user profile - in real app this would decode JWT
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

    # Ticket booking functionality
    ticket_bookings_db = []

    @app.route('/api/tickets/book', methods=['POST', 'OPTIONS'])
    def book_ticket():
        if request.method == 'OPTIONS':
            return '', 204

        try:
            logger.info("Ticket booking request received")
            logger.info(f"Request headers: {dict(request.headers)}")

            # Check for Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning("Ticket booking failed - no token provided")
                return {'success': False, 'message': 'Authentication required'}, 401

            data = request.get_json()
            logger.info(f"Ticket booking data: {data}")

            event_id = data.get('event_id')
            quantity = data.get('quantity', 1)
            user_email = data.get('user_email')  # From JWT token in real app

            if not event_id:
                return {'success': False, 'message': 'Event ID is required'}, 400

            # Find the event
            event = next((e for e in events_db if e['id'] == event_id), None)
            if not event:
                return {'success': False, 'message': 'Event not found'}, 404

            # Calculate total price
            total_price = event['ticket_price'] * quantity

            # Create booking
            booking = {
                'id': len(ticket_bookings_db) + 1,
                'event_id': event_id,
                'user_email': user_email or 'test@example.com',
                'quantity': quantity,
                'total_price': total_price,
                'status': 'CONFIRMED',
                'booking_date': __import__('datetime').datetime.now().isoformat(),
                'event_title': event['title']
            }

            ticket_bookings_db.append(booking)
            logger.info(f"Ticket booking successful: {booking}")

            return {
                'success': True,
                'message': f'Successfully booked {quantity} ticket(s) for {event["title"]}',
                'booking': booking
            }, 201

        except Exception as e:
            logger.error(f"Ticket booking error - {str(e)}")
            return {'success': False, 'message': 'Booking failed'}, 500

    @app.route('/api/tickets/user', methods=['GET', 'OPTIONS'])
    def get_user_tickets():
        if request.method == 'OPTIONS':
            return '', 204

        try:
            logger.info("User tickets request received")
            logger.info(f"Request headers: {dict(request.headers)}")

            # Check for Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning("User tickets failed - no token provided")
                return {'success': False, 'message': 'Authentication required'}, 401

            # In a real app, you'd decode the JWT to get user email
            # For now, return mock bookings
            user_bookings = [b for b in ticket_bookings_db if b['user_email'] == 'test@example.com']

            logger.info(f"User tickets retrieved: {len(user_bookings)} bookings")

            return {
                'success': True,
                'tickets': user_bookings
            }, 200

        except Exception as e:
            logger.error(f"User tickets error - {str(e)}")
            return {'success': False, 'message': 'Failed to retrieve tickets'}, 500

    @app.route('/api/debug', methods=['GET', 'OPTIONS'])
    def api_debug():
        if request.method == 'OPTIONS':
            return '', 204
        return {
            'success': True,
            'endpoints': [
                'GET/POST /api/events',
                'GET/PUT /api/events/<id>',
                'GET/POST /api/services',
                'PUT /api/services/<id>',
                'GET /api/notifications',
                'GET /api/dashboard/organizer',
                'GET /api/dashboard/vendor',
                'POST /api/auth/login',
                'POST /api/auth/register',
                'POST /api/auth/logout',
                'GET /api/auth/profile',
                'POST /api/tickets/book',
                'GET /api/tickets/user'
            ],
            'data_counts': {
                'events': len(events_db),
                'services': len(services_db),
                'notifications': len(notifications_db),
                'ticket_bookings': len(ticket_bookings_db)
            }
        }
    
    @app.errorhandler(404)
    def not_found(error):
        return {'success': False, 'error': 'Endpoint not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'success': False, 'error': 'Internal server error'}, 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(port=5555, debug=True)