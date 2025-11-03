#!/usr/bin/env python3
"""
EventRift Server Startup Script
Ensures all components are properly initialized and the server starts correctly
"""

import os
import sys
from flask import Flask
from flask_migrate import upgrade

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_app():
    """Create and configure the Flask application"""
    try:
        # Import the main app creation function
        from app import create_app as app_factory
        app = app_factory()
        return app
    except ImportError as e:
        print(f"Error importing app: {e}")
        # Fallback to basic app creation
        app = Flask(__name__)
        
        # Basic configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///eventrift.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
        
        # Initialize extensions
        from eventrift.extensions import db, migrate, jwt
        db.init_app(app)
        migrate.init_app(app, db)
        jwt.init_app(app)
        
        # Initialize routes
        from eventrift.routes import initialize_routes
        initialize_routes(app)
        
        return app

def initialize_database(app):
    """Initialize the database with tables"""
    with app.app_context():
        try:
            from eventrift.extensions import db
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Run any pending migrations
            try:
                upgrade()
                print("✅ Database migrations applied successfully")
            except Exception as e:
                print(f"⚠️  Migration warning: {e}")
                
        except Exception as e:
            print(f"❌ Database initialization error: {e}")

def main():
    """Main function to start the server"""
    print("🚀 Starting EventRift Server...")
    print("=" * 50)
    
    # Create the Flask app
    app = create_app()
    
    # Initialize database
    initialize_database(app)
    
    # Print available routes
    print("\n📋 Available Routes:")
    with app.app_context():
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
            print(f"   {methods:10} {rule.rule}")
    
    print("\n" + "=" * 50)
    print("🌐 Server starting on http://localhost:5555")
    print("📊 Dashboard endpoints available for all user roles:")
    print("   - Goer Dashboard: GET /api/dashboard (with Goer token)")
    print("   - Organizer Dashboard: GET /api/dashboard (with Organizer token)")
    print("   - Vendor Dashboard: GET /api/dashboard (with Vendor token)")
    print("   - Admin Dashboard: GET /api/dashboard (with Admin token)")
    print("\n🧪 Test endpoints:")
    print("   - Health Check: GET /api/test/health")
    print("   - Setup Test Data: POST /api/test/setup-test-data")
    print("   - List All Endpoints: GET /api/test/endpoints")
    print("\n🔐 Authentication:")
    print("   - Register: POST /auth/register")
    print("   - Login: POST /auth/login")
    print("   - Profile: GET /auth/profile")
    print("=" * 50)
    
    # Start the server
    try:
        port = int(os.environ.get('PORT', 5555))
        debug = os.environ.get('FLASK_ENV') == 'development'
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()