from flask import Flask
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

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    jwt.init_app(app)

    @app.route('/')
    def hello():
        return {'message': 'EventRift Server is running!'}

    return app

app = create_app()

if __name__ == '__main__':
    app.run(port=5555, debug=True)