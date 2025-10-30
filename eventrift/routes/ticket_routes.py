from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db # Assuming db is available
from app.models.ticket_attendance import Ticket, Attendance
from app.schemas.ticket_schemas import tickets_schema, ticket_schema
from sqlalchemy.orm import joinedload
from datetime import datetime

# Assuming User and Event models are available for relationships
# from app.models.user_models import User
# from app.models.event_models import Event 

ticket_bp = Blueprint('ticket_bp', __name__)
api = Api(ticket_bp)

class UserTicketListResource(Resource):
    @jwt_required()
    def get(self):
        """(Goer) Retrieves all tickets belonging to the authenticated user."""
        current_user_id = get_jwt_identity()
        
        # Eager load relationships to prevent N+1 queries
        tickets = Ticket.query.filter_by(user_id=current_user_id).options(
            joinedload(Ticket.attendance)
            # joinedload(Ticket.event), # Load event data
            # joinedload(Ticket.user)   # Load user data
        ).all()
        
        return jsonify(tickets_schema.dump(tickets)), 200

class TicketDetailResource(Resource):
    @jwt_required()
    def get(self, uuid):
        """(Goer) Retrieves a single ticket by its UUID for display (e.g., QR code view)."""
        current_user_id = get_jwt_identity()

        # Find the ticket by its unique UUID and ensure it belongs to the user
        ticket = Ticket.query.options(joinedload(Ticket.attendance)).filter_by(uuid=uuid, user_id=current_user_id).first()

        if not ticket:
            return {"message": "Ticket not found or access denied."}, 404

        return jsonify(ticket_schema.dump(ticket)), 200


class CheckInResource(Resource):
    # This route is protected and restricted to Organizer/Staff roles
    @jwt_required()
    def post(self):
        """
        (Organizer/Staff) Checks in a ticket using its QR code content (UUID).
        Input payload: {"qr_data": "base64_encoded_uuid"}
        """
        current_user_id = get_jwt_identity()
        # NOTE: Implement proper RBAC here (e.g., check if current_user_id has role 'Organizer' or 'Staff')
        
        data = request.get_json()
        qr_data = data.get('qr_data') # This is the Base64 encoded UUID from the frontend
        
        if not qr_data:
            return {"message": "QR data is required."}, 400

        try:
            # Decode the base64 QR data back to the original UUID string
            ticket_uuid = base64.b64decode(qr_data.encode()).decode()
        except Exception:
            return {"message": "Invalid QR code format."}, 400
        
        # 1. Find the ticket using the decoded UUID
        ticket = Ticket.query.options(joinedload(Ticket.attendance)).filter_by(uuid=ticket_uuid).first()

        if not ticket:
            return {"message": "Invalid ticket or ticket not found."}, 404
            
        # 2. Check ticket status (must be PAID)
        if ticket.status != 'PAID':
            return {"message": f"Ticket status is '{ticket.status}'. Cannot check in."}, 400

        # 3. Check attendance status
        attendance = ticket.attendance
        if not attendance:
            # Should not happen if ticket creation is correct, but handle defensively
            attendance = Attendance(ticket_id=ticket.id)
            db.session.add(attendance)
            db.session.commit()
            
        if attendance.is_checked_in:
            return {"message": f"Ticket already checked in at {attendance.checked_in_at.strftime('%Y-%m-%d %H:%M:%S')}."}, 400
            
        # 4. Perform check-in (BE-403)
        attendance.is_checked_in = True
        attendance.checked_in_at = datetime.utcnow()
        attendance.checked_in_by_user_id = current_user_id
        
        try:
            db.session.commit()
            return {"message": "Check-in successful!", "ticket": ticket_schema.dump(ticket)}, 200
        except Exception as e:
            db.session.rollback()
            print(f"Check-in failed: {e}")
            return {"message": "An error occurred during check-in."}, 500


# Register the resources with the API blueprint
api.add_resource(UserTicketListResource, '/user')
api.add_resource(TicketDetailResource, '/<string:uuid>')
api.add_resource(CheckInResource, '/checkin')
