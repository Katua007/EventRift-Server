from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import Config


db = SQLAlchemy()
migrate = Migrate()
api = Api()
jwt = JWTManager()

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    jwt.init_app(app)
    # Initialize SocketIO
    socketio.init_app(app)

    # Register API routes 
    from app.routes.user_routes import initialize_user_routes
    from app.routes.event_routes import initialize_event_routes # New Import
    initialize_user_routes(api)
    initialize_event_routes(api) # New registration
    # from app.routes.user_routes import initialize_user_routes
    # initialize_user_routes(api)

    return app

# SocketIO Event Handlers
@socketio.on('join_event_room')
def handle_join_event_room(data):
    """Allows a client to subscribe to a specific event ID for real-time updates."""
    event_id = data.get('event_id')
    room = f'event_{event_id}'
    join_room(room)
    # Logic to increment view count in DB/Redis could go here
    print(f"Client joined room: {room}")
    # Example: Emit the current (placeholder) view count to the joining client
    emit('view_count', {'count': 100}, room=room) 
    
@socketio.on('disconnect')
def test_disconnect():
    print("Client disconnected")

app = create_app()

if __name__ == '__main__':
    app.run(port=5555, debug=True)