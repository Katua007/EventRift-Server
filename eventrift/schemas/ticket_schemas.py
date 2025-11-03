from marshmallow import fields, Schema

class AttendanceSchema(Schema):
    """Schema for serializing Attendance details."""
    id = fields.Integer()
    ticket_id = fields.Integer()
    is_checked_in = fields.Boolean()
    checked_in_at = fields.DateTime()
    checked_in_by_user_id = fields.Integer()
    created_at = fields.DateTime()

class TicketSchema(Schema):
    """Schema for serializing Ticket details."""
    id = fields.Integer()
    uuid = fields.String()
    user_id = fields.Integer()
    event_id = fields.Integer()
    payment_id = fields.Integer()
    status = fields.String()
    ticket_type = fields.String()
    qr_code_data = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    
    # Include the computed QR data property (base64 encoded UUID)
    qr_code_content = fields.String(attribute='encoded_qr_data', dump_only=True)
    
    # Include attendance status details
    attendance = fields.Nested(AttendanceSchema, required=False)

# Instantiations
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
attendance_schema = AttendanceSchema()
