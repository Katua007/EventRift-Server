from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from app import db # Assuming 'db' is initialized in app/__init__.py
import uuid
import base64

class Ticket(db.Model):
    """Represents a ticket purchased for an event."""
    __tablename__ = 'tickets'

    # Core Fields
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_tickets_user_id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', name='fk_tickets_event_id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id', name='fk_tickets_payment_id'), nullable=False)
    
    # Ticket Status
    status = db.Column(db.String(20), default='PENDING', nullable=False) # e.g., PENDING, PAID, REFUNDED
    ticket_type = db.Column(db.String(50), default='General Admission')

    # Security & Check-in
    qr_code_data = db.Column(db.Text, nullable=True) # Stores the unique data for QR generation (e.g., UUID or encrypted payload)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # user = db.relationship("User", backref="tickets") # Assuming a User model exists
    # event = db.relationship("Event", backref="tickets") # Assuming an Event model exists
    attendance = db.relationship("Attendance", uselist=False, backref="ticket", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Ticket {self.uuid} for Event {self.event_id}>"

    # Hybrid property to generate QR data content (e.g., Base64 encoded UUID)
    @hybrid_property
    def encoded_qr_data(self):
        """Generates a secure, base64-encoded string for use in QR codes."""
        # Use the UUID and optionally a secret key (though standard UUID is usually enough)
        data_to_encode = f"{self.uuid}"
        return base64.b64encode(data_to_encode.encode()).decode()

    @encoded_qr_data.expression
    def encoded_qr_data(cls):
        # This is for querying, typically not needed for a computed value like this
        return cls.uuid # Fallback to UUID for expression-based queries

class Attendance(db.Model):
    """Tracks the check-in status of a ticket."""
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    
    # Relationship to Ticket
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', name='fk_attendance_ticket_id'), unique=True, nullable=False)
    
    # Attendance Status
    is_checked_in = db.Column(db.Boolean, default=False, nullable=False)
    checked_in_at = db.Column(db.DateTime, nullable=True)
    checked_in_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_attendance_checked_in_by'), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Attendance Ticket:{self.ticket_id} CheckedIn:{self.is_checked_in}>"
