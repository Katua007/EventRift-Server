"""
Simple models.py file for EventRift
"""

try:
    from eventrift.extensions import db
    from eventrift.models.user import User
    from eventrift.models.event import Event
    from eventrift.models.vendor_service import VendorService
    from eventrift.models.payment import Payment
    from eventrift.models.ticket_attendance import Ticket, Attendance
    from eventrift.models.stall_booking import StallType, StallPayment, StallBooking
except ImportError:
    # Fallback - create basic models
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
    
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(120), unique=True, nullable=False)
        username = db.Column(db.String(80), nullable=False)
        role = db.Column(db.String(20), default='Goer')
    
    class Event(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200), nullable=False)
        description = db.Column(db.Text)
        organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    class VendorService(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(200), nullable=False)
        vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

__all__ = ['db', 'User', 'Event', 'VendorService', 'Payment', 'Ticket', 'Attendance', 'StallType', 'StallPayment', 'StallBooking']