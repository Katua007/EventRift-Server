from marshmallow import fields, Schema
from app.models.ticket_attendance import Ticket, Attendance # Assuming models are importable
from app import ma # Assuming 'ma' (Marshmallow) is initialized in app/__init__.py

class AttendanceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Attendance
        # Do not include sensitive foreign keys in public view
        exclude = ('checked_in_by_user_id',) 
        load_instance = True
        sqla_session = db.session

    checked_in_by_user = fields.Nested('UserSchema', only=('id', 'username'), required=False)


class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        # Exclude sensitive fields like raw UUID, include the computed QR data
        exclude = ('uuid', 'payment_id', 'qr_code_data') 
        load_instance = True
        sqla_session = db.session

    # Include the computed QR data property (base64 encoded UUID)
    qr_code_content = fields.String(attribute='encoded_qr_data', dump_only=True)

    # Relationships (Assuming you have UserSchema and EventSchema defined elsewhere)
    user = fields.Nested('UserSchema', only=('id', 'username', 'email')) 
    event = fields.Nested('EventSchema', only=('id', 'name', 'start_date'))
    
    # Include attendance status details
    attendance = fields.Nested(AttendanceSchema, required=False)

# Instantiations
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
attendance_schema = AttendanceSchema()
