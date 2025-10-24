from datetime import datetime
from app.extensions import db # Assuming you initialize SQLAlchemy in app/extensions.py or app/__init__.py

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False) # Store date and time together
    ticket_price = db.Column(db.Numeric(10, 2), nullable=False) # Price in KES
    capacity = db.Column(db.Integer, nullable=False)
    
    image_url = db.Column(db.String(500), nullable=True) # Optional image link
    is_published = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organizer = db.relationship('User', backref=db.backref('events', lazy=True))
    # Add relationship to tickets/bookings when those models are created

    def __repr__(self):
        return f"<Event {self.name}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
