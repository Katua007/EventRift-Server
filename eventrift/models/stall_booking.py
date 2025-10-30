from datetime import datetime
# Assuming 'db' is initialized in app/__init__.py
from app import db 
import uuid 

# NOTE: Assuming you have 'users' and 'events' tables defined elsewhere for foreign keys

class StallType(db.Model):
    """Defines different types of stalls (e.g., Food, Merch, Premium) available at events."""
    __tablename__ = 'stall_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False) # Price per stall in KES
    size = db.Column(db.String(50), nullable=True) # e.g., '3m x 3m'
    description = db.Column(db.Text)
    
    # Relationship to StallBooking
    stall_bookings = db.relationship('StallBooking', backref='stall_type', lazy=True)

    def __repr__(self):
        return f"<StallType {self.name} - KES {self.price}>"

class StallPayment(db.Model):
    """Tracks the M-Pesa payment transaction for a stall booking."""
    __tablename__ = 'stall_payments'

    id = db.Column(db.Integer, primary_key=True)
    
    # Unique reference generated during initiation (Crucial for callback matching)
    checkout_request_id = db.Column(db.String(50), unique=True, nullable=True)
    merchant_request_id = db.Column(db.String(50), nullable=True)

    # Core payment details
    amount = db.Column(db.Float, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    status = db.Column(db.String(20), default='PENDING', nullable=False) # PENDING, PAID, FAILED, CANCELLED
    
    # Confirmation details
    mpesa_receipt_number = db.Column(db.String(20), unique=True, nullable=True)
    transaction_date = db.Column(db.DateTime, nullable=True) # Transaction completion time
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to the actual booking (One-to-One)
    # The 'booking' backref is defined on StallBooking model
    
    def __repr__(self):
        return f"<StallPayment {self.id} - Status: {self.status}>"

class StallBooking(db.Model):
    """Represents a confirmed booking of a stall by a vendor."""
    __tablename__ = 'stall_bookings'

    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Vendor (User) who booked
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    stall_type_id = db.Column(db.Integer, db.ForeignKey('stall_types.id'), nullable=False)
    
    # Payment relationship (One-to-One)
    payment_id = db.Column(db.Integer, db.ForeignKey('stall_payments.id'), unique=True, nullable=True)
    
    # Booking details
    status = db.Column(db.String(20), default='PENDING_PAYMENT', nullable=False) # PENDING_PAYMENT, CONFIRMED, CANCELLED
    business_name = db.Column(db.String(150), nullable=False)
    products_offered = db.Column(db.Text, nullable=True)
    stall_location = db.Column(db.String(100), nullable=True) # Assigned location once confirmed
    
    # Relationships
    payment = db.relationship('StallPayment', backref='booking', uselist=False) # Use uselist=False for one-to-one
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<StallBooking {self.id} for Event {self.event_id} - {self.status}>"
