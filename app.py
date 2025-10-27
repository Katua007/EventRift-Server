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
    
    @app.route('/api/test')
    def test_cors():
        return {
            'success': True,
            'message': 'CORS is working!',
            'frontend_url': 'https://event-rift-client.vercel.app'
        }
    
    @app.route('/api/events', methods=['GET', 'OPTIONS'])
    def get_events():
        if request.method == 'OPTIONS':
            return '', 200
            
        events = [
            {'id': 1, 'title': 'Tech Conference 2024', 'date': '2024-06-15', 'location': 'Nairobi'},
            {'id': 2, 'title': 'Music Festival', 'date': '2024-07-20', 'location': 'Mombasa'}
        ]
        return {'success': True, 'events': events}
    
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

    return app

app = create_app()

if __name__ == '__main__':
    app.run(port=5555, debug=True)