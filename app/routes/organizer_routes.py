from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.event import Event
from app.models.user import User
from app.schemas.event_schemas import event_schema, events_schema
from app import db
from datetime import datetime

organizer_bp = Blueprint('organizer_bp', __name__)
api = Api(organizer_bp)

class OrganizerEventListResource(Resource):
    @jwt_required()
    def get(self):
        """Get all events organized by the current user."""
        current_user_id = get_jwt_identity()

        # Verify user is an organizer
        user = User.query.get(current_user_id)
        if not user or user.role != 'Organizer':
            return {"message": "Access denied. Organizer role required."}, 403

        events = Event.query.filter_by(organizer_id=current_user_id).all()
        return jsonify(events_schema.dump(events)), 200

    @jwt_required()
    def post(self):
        """Create a new event."""
        current_user_id = get_jwt_identity()

        # Verify user is an organizer
        user = User.query.get(current_user_id)
        if not user or user.role != 'Organizer':
            return {"message": "Access denied. Organizer role required."}, 403

        data = request.get_json()

        required_fields = ['name', 'description', 'date_start', 'location_address', 'ticket_price', 'capacity']
        if not all(field in data for field in required_fields):
            return {"message": "Missing required fields."}, 400

        try:
            new_event = Event(
                organizer_id=current_user_id,
                name=data['name'],
                description=data['description'],
                date_start=datetime.fromisoformat(data['date_start']),
                location_address=data['location_address'],
                ticket_price=data['ticket_price'],
                capacity=data['capacity'],
                image_url=data.get('image_url'),
                status=data.get('status', 'Draft')
            )

            db.session.add(new_event)
            db.session.commit()

            return jsonify(event_schema.dump(new_event)), 201

        except Exception as e:
            db.session.rollback()
            return {"message": f"Error creating event: {str(e)}"}, 500

class OrganizerEventDetailResource(Resource):
    @jwt_required()
    def get(self, event_id):
        """Get a specific event by ID."""
        current_user_id = get_jwt_identity()

        # Verify user is an organizer
        user = User.query.get(current_user_id)
        if not user or user.role != 'Organizer':
            return {"message": "Access denied. Organizer role required."}, 403

        event = Event.query.filter_by(id=event_id, organizer_id=current_user_id).first()
        if not event:
            return {"message": "Event not found or access denied."}, 404

        return jsonify(event_schema.dump(event)), 200

    @jwt_required()
    def put(self, event_id):
        """Update an event."""
        current_user_id = get_jwt_identity()

        # Verify user is an organizer
        user = User.query.get(current_user_id)
        if not user or user.role != 'Organizer':
            return {"message": "Access denied. Organizer role required."}, 403

        event = Event.query.filter_by(id=event_id, organizer_id=current_user_id).first()
        if not event:
            return {"message": "Event not found or access denied."}, 404

        data = request.get_json()

        try:
            # Update fields if provided
            if 'name' in data:
                event.name = data['name']
            if 'description' in data:
                event.description = data['description']
            if 'date_start' in data:
                event.date_start = datetime.fromisoformat(data['date_start'])
            if 'location_address' in data:
                event.location_address = data['location_address']
            if 'ticket_price' in data:
                event.ticket_price = data['ticket_price']
            if 'capacity' in data:
                event.capacity = data['capacity']
            if 'image_url' in data:
                event.image_url = data['image_url']
            if 'status' in data:
                event.status = data['status']

            db.session.commit()

            return jsonify(event_schema.dump(event)), 200

        except Exception as e:
            db.session.rollback()
            return {"message": f"Error updating event: {str(e)}"}, 500

    @jwt_required()
    def delete(self, event_id):
        """Delete an event."""
        current_user_id = get_jwt_identity()

        # Verify user is an organizer
        user = User.query.get(current_user_id)
        if not user or user.role != 'Organizer':
            return {"message": "Access denied. Organizer role required."}, 403

        event = Event.query.filter_by(id=event_id, organizer_id=current_user_id).first()
        if not event:
            return {"message": "Event not found or access denied."}, 404

        try:
            db.session.delete(event)
            db.session.commit()
            return {"message": "Event deleted successfully."}, 200

        except Exception as e:
            db.session.rollback()
            return {"message": f"Error deleting event: {str(e)}"}, 500

# Register the resources with the API blueprint
api.add_resource(OrganizerEventListResource, '/events')
api.add_resource(OrganizerEventDetailResource, '/events/<int:event_id>')