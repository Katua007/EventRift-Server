from app import db
from datetime import datetime

class EventCategory(db.Model):
    __tablename__ = 'event_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with events
    events = db.relationship('Event', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<EventCategory {self.name}>'