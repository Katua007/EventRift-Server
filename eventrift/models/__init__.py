from eventrift.extensions import db # Import the shared SQLAlchemy instance

# Import models so they are registered with SQLAlchemy
from .user import User
from .event import Event
from .vendor_service import VendorService
from .payment import Payment
from .ticket_attendance import Ticket, Attendance
from .stall_booking import StallType, StallPayment, StallBooking

# Export all models
__all__ = [
    'db', 'User', 'Event', 'VendorService', 'Payment',
    'Ticket', 'Attendance', 'StallType', 'StallPayment', 'StallBooking'
]