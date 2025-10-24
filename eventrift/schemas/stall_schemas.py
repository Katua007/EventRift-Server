from marshmallow import fields, Schema
from app.models.stall_booking import StallType, StallPayment, StallBooking
# Assuming 'ma' (Marshmallow) and 'db' are initialized in app/__init__.py
from app import ma 
from app import db 

class StallTypeSchema(ma.SQLAlchemyAutoSchema):
    """Schema for serializing StallType details."""
    class Meta:
        model = StallType
        load_instance = True
        sqla_session = db.session
        fields = ('id', 'name', 'price', 'size', 'description')

class StallPaymentSchema(ma.SQLAlchemyAutoSchema):
    """Schema for serializing StallPayment details."""
    class Meta:
        model = StallPayment
        # Exclude sensitive M-Pesa IDs from general public view
        exclude = ('checkout_request_id', 'merchant_request_id', 'id')
        load_instance = True
        sqla_session = db.session

class StallBookingSchema(ma.SQLAlchemyAutoSchema):
    """Schema for serializing the complete StallBooking record."""
    class Meta:
        model = StallBooking
        load_instance = True
        sqla_session = db.session
        # Include foreign keys for simplicity, assuming they are needed client-side
        include_fk = True 
        
    # Nested relationships for rich data retrieval
    # These fields link the booking to its payment and stall type details.
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
