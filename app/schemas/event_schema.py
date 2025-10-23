from marshmallow import Schema, fields, validate, post_load
from app.models.event import Event

class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    organizer_id = fields.Int(dump_only=True) # Organizer ID is set on the backend from auth token
    
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    description = fields.Str(required=True, validate=validate.Length(min=10))
    location = fields.Str(required=True, validate=validate.Length(min=5, max=200))
    
    # Use DateTime field for ISO 8601 string input
    date_time = fields.DateTime(required=True, format="iso") 
    
    # Use Decimal for monetary values
    ticket_price = fields.Decimal(
        required=True, 
        places=2, 
        validate=validate.Range(min=0.00, error="Price must be non-negative.")
    )
    
    capacity = fields.Int(
        required=True, 
        validate=validate.Range(min=10, error="Capacity must be at least 10.")
    )
    
    image_url = fields.Url(allow_none=True, required=False)
    is_published = fields.Bool(dump_only=True)
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @post_load
    def make_event(self, data, **kwargs):
        """Turn validated data into an Event model instance."""
        return Event(**data)

# Instance for single event serialization/deserialization
event_schema = EventSchema()
# Instance for list of events serialization
events_schema = EventSchema(many=True)
