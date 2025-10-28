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
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
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
    CORS(app, 
         origins=[
             'http://localhost:3000', 
             'http://localhost:5173',
             'http://localhost:5174',
             'https://event-rift-client.vercel.app',
             'https://*.vercel.app'
         ],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    jwt.init_app(app)



    @app.route('/')
    def hello():
        return {'message': 'EventRift Server is running!'}
    
    @app.route('/api/health')
    def health():
        return {'status': 'healthy', 'message': 'EventRift API is running'}
    
    @app.route('/api/test', methods=['GET', 'OPTIONS'])
    def test_cors():
        if request.method == 'OPTIONS':
            return '', 200
        return {
            'success': True,
            'message': 'CORS is working!',
            'frontend_url': 'https://event-rift-client.vercel.app',
            'backend_url': request.url_root
        }
    
    @app.route('/api/debug', methods=['GET', 'OPTIONS'])
    def debug_info():
        if request.method == 'OPTIONS':
            return '', 200
        return {
            'success': True,
            'endpoints': [
                'GET /api/events',
                'GET /api/events/<id>',
                'POST /api/auth/login',
                'POST /api/auth/register',
                'GET /api/auth/profile',
                'GET /api/health',
                'GET /api/test',
                'GET /api/debug'
            ],
            'cors_origins': [
                'https://event-rift-client.vercel.app',
                'http://localhost:3000',
                'http://localhost:5173',
                'http://localhost:5174'
            ],
            'server_time': str(__import__('datetime').datetime.now())
        }
    
    @app.errorhandler(404)
    def not_found(error):
        return {'success': False, 'error': 'Endpoint not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'success': False, 'error': 'Internal server error'}, 500
    
    @app.route('/api/events', methods=['GET', 'OPTIONS'])
    def get_events():
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            events = [
                {
                    'id': 1, 
                    'title': 'Tech Conference 2024', 
                    'description': 'Annual technology conference',
                    'date': '2024-06-15', 
                    'location': 'Nairobi',
                    'price': 5000,
                    'image': 'https://via.placeholder.com/400x300'
                },
                {
                    'id': 2, 
                    'title': 'Music Festival', 
                    'description': 'Live music and entertainment',
                    'date': '2024-07-20', 
                    'location': 'Mombasa',
                    'price': 3000,
                    'image': 'https://via.placeholder.com/400x300'
                }
            ]
            return {'success': True, 'events': events}
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @app.route('/api/events/<int:event_id>', methods=['GET', 'OPTIONS'])
    def get_event(event_id):
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            event = {
                'id': event_id,
                'title': f'Event {event_id}',
                'description': 'Event description',
                'date': '2024-06-15',
                'location': 'Nairobi',
                'price': 5000,
                'image': 'https://via.placeholder.com/400x300'
            }
            return {'success': True, 'event': event}
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
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
    
    @app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
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
    
    @app.route('/api/auth/profile', methods=['GET', 'OPTIONS'])
    def get_profile():
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            from flask_jwt_extended import jwt_required, get_jwt_identity
            
            # Check for Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'success': False, 'message': 'No token provided'}, 401
            
            # Mock user profile (replace with actual JWT verification)
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

    return app

app = create_app()

if __name__ == '__main__':
    app.run(port=5555, debug=True)