from marshmallow import Schema, fields

class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    organizer_id = fields.Int(required=True)
    name = fields.Str(required=True)
    description = fields.Str()
    date_start = fields.DateTime(required=True)
    location_address = fields.Str(required=True)
    ticket_price = fields.Decimal(required=True)
    capacity = fields.Int(required=True)
    image_url = fields.Str()
    status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

event_schema = EventSchema()
events_schema = EventSchema(many=True)