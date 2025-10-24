from app.models import db
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    _password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Goer') # Role-Based Access Control
    
    # Vendor specific fields
    license_number = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships (Simplified for base)
    events_organized = db.relationship('Event', backref='organizer', lazy=True)
    
    @hybrid_property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'