from flask import Blueprint, request
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime # Import datetime for filtering active events
from sqlalchemy import or_ # Import or_ for complex filtering

from app.schemas.event_schema import event_schema, events_schema # Import the list schema
from app.models.event import Event # Import the Event model
from app.decorators import requires_roles 
from app.extensions import db # Assuming db is initialized here or passed via extensions

# Create a Blueprint for event routes
events_bp = Blueprint('events_bp', __name__)
api = Api(events_bp)

class EventListResource(Resource):
    
    # BE-205: GET /api/events (Publicly Accessible)
    def get(self):
        """Returns a list of active (published, future-dated) events."""
        try:
            # 1. Define 'Active' criteria: 
            #    - is_published must be True
            #    - date_time must be in the future (greater than current datetime)
            
            current_time = datetime.utcnow()
            
            active_events = Event.query.filter(
                Event.is_published == True,
                Event.date_time > current_time
            ).order_by(Event.date_time.asc()).all()
            
            # 2. Serialize the list of events using the many=True schema instance
            result = events_schema.dump(active_events)
            
            return {
                "success": True,
                "message": "Active events retrieved successfully.",
                "events": result
            }, 200

        except Exception as e:
            print(f"Error fetching active events: {e}")
            return {"success": False, "message": "An unexpected error occurred while fetching events."}, 500

    # BE-204: POST /api/events (Organizer Required)
    @jwt_required()
    @requires_roles('Organizer') 
    def post(self):
        """Creates a new event (Organizer role required)."""
        
        current_user_id = get_jwt_identity()
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400

        try:
            # 1. Validate and deserialize input data
            validated_data = event_schema.load(json_data)
            
            # 2. Create Event instance and set organizer_id
            new_event = Event(**validated_data)
            new_event.organizer_id = current_user_id 
            
            # 3. Save the new event to the database
            new_event.save() 
            
            # 4. Serialize the created object and return response
            result = event_schema.dump(new_event)
            return {
                "success": True, 
                "message": "Event created successfully.", 
                "event": result
            }, 201

        except ValidationError as err:
            return {"success": False, "errors": err.messages}, 422
            
        except Exception as e:
            print(f"Error creating event: {e}")
            return {"success": False, "message": "An unexpected error occurred."}, 500

# Register the resource with the API blueprint
api.add_resource(EventListResource, '/events')
