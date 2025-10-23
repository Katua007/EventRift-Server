from flask import Blueprint, request
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.schemas.event_schema import event_schema # Import the single schema instance
# from app.models.user import User # Assuming User model is needed for authentication
from app.models.event import Event # Import the Event model
from app.decorators import requires_roles # Assuming this is the RBAC decorator

# Create a Blueprint for event routes
events_bp = Blueprint('events_bp', __name__)
api = Api(events_bp)

class EventListResource(Resource):
    
    # GET /events (Placeholder for listing all events)
    def get(self):
        # Implementation for listing events goes here (later task BE-203)
        return {"message": "Event list endpoint. GET not yet fully implemented."}, 200

    @jwt_required()
    @requires_roles('Organizer') # <-- RBAC RESTRICTION (BE-204 Requirement)
    def post(self):
        """Creates a new event (Organizer role required)."""
        
        # 1. Get the current user ID from the JWT token
        current_user_id = get_jwt_identity()

        # 2. Get data from the request
        json_data = request.get_json()
        if not json_data:
            return {'message': 'No input data provided'}, 400

        try:
            # 3. Validate and deserialize input data
            validated_data = event_schema.load(json_data)
            
            # 4. Create Event instance and set organizer_id from auth token
            new_event = Event(**validated_data)
            new_event.organizer_id = current_user_id # Set the ID from the authenticated user
            
            # 5. Save the new event to the database
            new_event.save() 
            
            # 6. Serialize the created object and return response
            result = event_schema.dump(new_event)
            return {
                "success": True, 
                "message": "Event created successfully.", 
                "event": result
            }, 201

        except ValidationError as err:
            # Return detailed validation errors
            return {"success": False, "errors": err.messages}, 422
