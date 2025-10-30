from eventrift.routes.event_routes import events_bp
from eventrift.routes.vendor_routes import initialize_vendor_routes
from eventrift.routes.auth_routes import auth_bp
from eventrift.routes.user_routes import user_bp
=======
from eventrift.routes.auth_routes import auth_bp
from eventrift.routes.user_routes import user_bp
>>>>>>> 56a7d977e77340592b978f8475033ef3fb3b56f3

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

    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(user_bp, url_prefix='')
>>>>>>> 56a7d977e77340592b978f8475033ef3fb3b56f3
=======
    # Register blueprints
    app.register_blueprint(events_bp, url_prefix='')
    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(user_bp, url_prefix='')
=======
    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(user_bp, url_prefix='')
>>>>>>> 56a7d977e77340592b978f8475033ef3fb3b56f3

    # Initialize vendor routes
    initialize_vendor_routes(api)
=======
from flask import Flask, request
from flask_cors import CORS
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the proper database models and routes
from eventrift.config import Config
from eventrift.extensions import db, migrate, api, jwt
from eventrift.routes.event_routes import events_bp
from eventrift.routes.vendor_routes import initialize_vendor_routes
from eventrift.routes.auth_routes import auth_bp
from eventrift.routes.user_routes import user_bp

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

    # Register blueprints
    app.register_blueprint(events_bp, url_prefix='')
    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(user_bp, url_prefix='')

    # Initialize vendor routes
    initialize_vendor_routes(api)
=======
from eventrift.routes.event_routes import events_bp
from eventrift.routes.vendor_routes import initialize_vendor_routes
from eventrift.routes.auth_routes import auth_bp
from eventrift.routes.user_routes import user_bp
=======
from eventrift.routes.auth_routes import auth_bp
from eventrift.routes.user_routes import user_bp
>>>>>>> 56a7d977e77340592b978f8475033ef3fb3b56f3

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

    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(user_bp, url_prefix='')
>>>>>>> 56a7d977e77340592b978f8475033ef3fb3b56f3
=======
    # Register blueprints
    app.register_blueprint(events_bp, url_prefix='')
    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(user_bp, url_prefix='')
=======
    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(user_bp, url_prefix='')
>>>>>>> 56a7d977e77340592b978f8475033ef3fb3b56f3

    # Initialize vendor routes
    initialize_vendor_routes(api)



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

    return app

app = create_app()

if __name__ == '__main__':
    app.run(port=5555, debug=True)