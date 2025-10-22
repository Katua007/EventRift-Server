from app.models import db

class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    date_start = db.Column(db.DateTime, nullable=False)
    location_address = db.Column(db.String(255), nullable=False)
    
    ticket_price = db.Column(db.Numeric(10, 2), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    
    image_url = db.Column(db.String(255)) # Cloudinary URL
    status = db.Column(db.String(20), default='Draft') 
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Event {self.name}>'