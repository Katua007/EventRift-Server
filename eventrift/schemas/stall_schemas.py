from marshmallow import fields, Schema
from eventrift.models.stall_booking import StallType, StallPayment, StallBooking
from eventrift.extensions import db
try:
    from flask_marshmallow import Marshmallow
    ma = Marshmallow()
except ImportError:
    ma = None 

class StallTypeSchema(Schema):
    """Schema for serializing StallType details."""
    id = fields.Integer()
    name = fields.String()
    price = fields.Float()
    size = fields.String()
    description = fields.String()

class StallPaymentSchema(Schema):
    """Schema for serializing StallPayment details."""
    status = fields.String()
    mpesa_receipt_number = fields.String()
    amount = fields.Float()
    phone_number = fields.String()
    transaction_date = fields.DateTime()
    created_at = fields.DateTime()

class StallBookingSchema(Schema):
    """Schema for serializing the complete StallBooking record."""
    id = fields.Integer()
    vendor_id = fields.Integer()
    event_id = fields.Integer()
    stall_type_id = fields.Integer()
    payment_id = fields.Integer()
    status = fields.String()
    business_name = fields.String()
    products_offered = fields.String()
    stall_location = fields.String()
    created_at = fields.DateTime()
    
    # Nested relationships for rich data retrieval
    stall_type = fields.Nested(StallTypeSchema, only=('name', 'price', 'size'))
    payment = fields.Nested(StallPaymentSchema, only=('status', 'mpesa_receipt_number', 'amount'))
    
    # NOTE: Placeholder fields for cross-model relationships (User and Event)
    # vendor = fields.Nested('UserSchema', only=('id', 'username'))
    # event = fields.Nested('EventSchema', only=('id', 'name'))

# Instantiations for single and list responses
stall_type_schema = StallTypeSchema()
stall_types_schema = StallTypeSchema(many=True)
stall_booking_schema = StallBookingSchema()
stall_bookings_schema = StallBookingSchema(many=True)
