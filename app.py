from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_jwt_extended import JWTManager
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()
api = Api()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    jwt.init_app(app)

    # Register API routes 
    from app.routes.user_routes import initialize_user_routes
    from app.routes.event_routes import initialize_event_routes # New Import
    initialize_user_routes(api)
    initialize_event_routes(api) # New registration
    # from app.routes.user_routes import initialize_user_routes
    # initialize_user_routes(api)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(port=5555, debug=True)