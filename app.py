from flask import Flask, request
from flask_cors import CORS
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5174')
    CORS(app,
          origins=[
              'http://localhost:3000',
              'http://localhost:5173',
              'http://localhost:5174',
              frontend_url,
              'https://*.vercel.app',
              'https://event-rift-client.vercel.app'
          ],
          methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
          allow_headers=['Content-Type', 'Authorization'],
          supports_credentials=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    jwt.init_app(app)

    # Register blueprints if available
    try:
        from eventrift.routes.event_routes import events_bp
        app.register_blueprint(events_bp, url_prefix='/')
    except ImportError:
        pass

    # Initialize routes
    try:
        from eventrift.routes import initialize_routes
        initialize_routes(app)
    except ImportError:
        pass

    # Global storage
    events_db = [
        {
            'id': 1, 
            'title': 'Tech Conference 2024', 
            'description': 'Annual technology conference',
            'date': '2024-06-15',
            'time': '09:00',
            'location': 'Nairobi',
            'theme': 'Innovation',
            'category': 'Technology',
            'dress_code': 'Business Casual',
            'ticket_price': 5000,
            'image': 'https://via.placeholder.com/400x300',
            'organizer_id': 'organizer@example.com'
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
        if request.method == 'OPTIONS':
            return '', 200
        
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
            return '', 200
        
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
        if request.method == 'OPTIONS':
            return '', 200
            
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            from flask_jwt_extended import create_access_token
            access_token = create_access_token(identity=email)
            return {
                'success': True,
                'access_token': access_token,
                'user': {'email': email, 'role': 'user'}
            }
        return {'success': False, 'message': 'Invalid credentials'}, 401
    
    @app.route('/auth/register', methods=['POST', 'OPTIONS'])
    def register():
        if request.method == 'OPTIONS':
            return '', 200
            
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name') or data.get('username')
        
        if email and password and name:
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': {'email': email, 'name': name, 'role': 'user'}
            }, 201
        return {'success': False, 'message': 'Missing required fields'}, 400
    
    @app.route('/auth/profile', methods=['GET', 'OPTIONS'])
    def get_profile():
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            # Check for Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'success': False, 'message': 'No token provided'}, 401
            
            # Mock user profile
            return {
                'success': True,
                'user': {
                    'id': 1,
                    'email': 'user@example.com',
                    'name': 'User Name',
                    'role': 'user'
                }
            }
        except Exception as e:
            return {'success': False, 'message': 'Invalid token'}, 401
    
    @app.route('/services', methods=['GET', 'POST', 'OPTIONS'])
    def handle_services():
        if request.method == 'OPTIONS':
            return '', 200
        
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
            return '', 200
        
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
            return '', 200
        return {'success': True, 'notifications': notifications_db}
    
    @app.route('/dashboard/organizer', methods=['GET', 'OPTIONS'])
    def organizer_dashboard():
        if request.method == 'OPTIONS':
            return '', 200
        
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
            return '', 200

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
            return '', 200

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
        if request.method == 'OPTIONS':
            return '', 200
            
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            from flask_jwt_extended import create_access_token
            access_token = create_access_token(identity=email)
            return {
                'success': True,
                'access_token': access_token,
                'user': {'email': email, 'role': 'user'}
            }
        return {'success': False, 'message': 'Invalid credentials'}, 401
    
    @app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
    def api_register():
        if request.method == 'OPTIONS':
            return '', 200
            
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name') or data.get('username')
        
        if email and password and name:
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': {'email': email, 'name': name, 'role': 'user'}
            }, 201
        return {'success': False, 'message': 'Missing required fields'}, 400
    
    @app.route('/test', methods=['GET', 'OPTIONS'])
    def test_cors():
        if request.method == 'OPTIONS':
            return '', 200
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
    
    @app.route('/debug', methods=['GET', 'OPTIONS'])
    def debug_info():
        if request.method == 'OPTIONS':
            return '', 200
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
                'GET /api/auth/profile'
            ],
            'data_counts': {
                'events': len(events_db),
                'services': len(services_db),
                'notifications': len(notifications_db)
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