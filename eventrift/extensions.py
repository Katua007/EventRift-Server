from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
api = Api()
jwt = JWTManager()

# Optional SocketIO import - only initialize if available
try:
    from flask_socketio import SocketIO
    socketio = SocketIO(cors_allowed_origins="*")
except ImportError:
    socketio = None