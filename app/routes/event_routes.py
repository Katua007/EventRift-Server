from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.event import Event
from app.models import db
from app.schemas.event_schema import event_schema, events_schema
from app.routes.user_routes import role_required # Import the RBAC decorator

class EventListResource(Resource):
    @jwt_required()
    @role_required('Organizer') # Only Organizers can create events (O-1)
    def post(self):
        data = request.get_json()
        
        try:
            # Load and validate data using Marshmallow
            validated_data = event_schema.load(data)
            
            # Ensure organizer_id matches token identity for security
            if validated_data['organizer_id'] != get_jwt_identity():
                 return {'message': 'Unauthorized: Organizer ID mismatch'}, 403

            new_event = Event(**validated_data)
            db.session.add(new_event)
            db.session.commit()
            
            return event_schema.dump(new_event), 201
            
        except Exception as e:
            db.session.rollback()
            return {'message': f'Validation or database error: {str(e)}'}, 400

    def get(self):
        # Public route: List all active events
        events = Event.query.filter_by(status='Active').all()
        return events_schema.dump(events), 200

def initialize_event_routes(api):
    api.add_resource(EventListResource, '/events')
    # Add EventResource here later (GET/PUT/DELETE for a single event)