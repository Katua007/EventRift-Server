from marshmallow import fields, Schema
# from app.models.ticket_attendance import Ticket, Attendance # Assuming models are importable - MOVED TO AVOID CIRCULAR IMPORT
# from app import ma # Assuming 'ma' (Marshmallow) is initialized in app/__init__.py - MOVED TO AVOID CIRCULAR IMPORT

class AttendanceSchema(Schema):
    id = fields.Int(dump_only=True)
    ticket_id = fields.Int(dump_only=True)
    is_checked_in = fields.Bool()
    checked_in_at = fields.DateTime()
    checked_in_by_user_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    checked_in_by_user = fields.Nested('UserSchema', only=('id', 'username'), required=False)


class TicketSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    event_id = fields.Int(dump_only=True)
    payment_id = fields.Int(dump_only=True)
    status = fields.Str()
    ticket_type = fields.Str()
    uuid = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    # Include the computed QR data property (base64 encoded UUID)
    qr_code_content = fields.Str(dump_only=True)

    # Relationships (Assuming you have UserSchema and EventSchema defined elsewhere)
    user = fields.Nested('UserSchema', only=('id', 'username', 'email'))
    event = fields.Nested('EventSchema', only=('id', 'name', 'start_date'))

    # Include attendance status details
    attendance = fields.Nested(AttendanceSchema, required=False)

# Instantiations
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
attendance_schema = AttendanceSchema()
