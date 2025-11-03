# Import database instance from extensions
from eventrift.extensions import db
# Import datetime for timestamps
from datetime import datetime

# EventCategory model represents different types of events (Music, Sports, etc.)
class EventCategory(db.Model):
    # Database table name
    __tablename__ = 'event_categories'

    # Primary key - unique identifier for each category
    id = db.Column(db.Integer, primary_key=True)
    # Category name (required, unique, max 100 characters)
    name = db.Column(db.String(100), nullable=False, unique=True)
    # Optional description of the category
    description = db.Column(db.Text)
    # Timestamp when category was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Timestamp when category was last updated
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship: one category can have many events
    events = db.relationship('Event', backref='category', lazy=True)

    # String representation for debugging
    def __repr__(self):
        return f'<EventCategory {self.name}>'