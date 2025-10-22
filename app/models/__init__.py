from app.app import db # Import the shared SQLAlchemy instance

# Import models so they are registered with SQLAlchemy
from .user import User
from .event import Event

# Add other models here later (Ticket, StallBooking, etc.)