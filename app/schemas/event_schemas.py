from marshmallow import fields, Schema
# from app import ma # Assuming 'ma' (Marshmallow) is initialized in app/__init__.py - MOVED TO AVOID CIRCULAR IMPORT

class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    organizer_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    date_start = fields.DateTime(required=True)
    location_address = fields.Str(required=True)
    ticket_price = fields.Float(required=True)
    capacity = fields.Int(required=True)
    image_url = fields.Str()
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True)

    # Relationships
    organizer = fields.Nested('UserSchema', only=('id', 'username', 'email'), dump_only=True)

# Instantiations
event_schema = EventSchema()
events_schema = EventSchema(many=True)