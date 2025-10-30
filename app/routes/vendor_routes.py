from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.stall_booking import StallBooking
from app.models.user import User
from app.schemas.stall_schemas import stall_booking_schema, stall_bookings_schema
from app import db
from datetime import datetime

vendor_bp = Blueprint('vendor_bp', __name__)
api = Api(vendor_bp)

class VendorStallListResource(Resource):
    @jwt_required()
    def get(self):
        """Get all stall bookings for the current vendor."""
        current_user_id = get_jwt_identity()

        # Verify user is a vendor
        user = User.query.get(current_user_id)
        if not user or user.role != 'Vendor':
            return {"message": "Access denied. Vendor role required."}, 403

        stall_bookings = StallBooking.query.filter_by(vendor_id=current_user_id).all()
        return jsonify(stall_bookings_schema.dump(stall_bookings)), 200

    @jwt_required()
    def post(self):
        """Create a new stall booking request."""
        current_user_id = get_jwt_identity()

        # Verify user is a vendor
        user = User.query.get(current_user_id)
        if not user or user.role != 'Vendor':
            return {"message": "Access denied. Vendor role required."}, 403

        data = request.get_json()

        required_fields = ['event_id', 'stall_type', 'description']
        if not all(field in data for field in required_fields):
            return {"message": "Missing required fields."}, 400

        try:
            new_booking = StallBooking(
                vendor_id=current_user_id,
                event_id=data['event_id'],
                stall_type=data['stall_type'],
                description=data['description'],
                status='Pending'
            )

            db.session.add(new_booking)
            db.session.commit()

            return jsonify(stall_booking_schema.dump(new_booking)), 201

        except Exception as e:
            db.session.rollback()
            return {"message": f"Error creating stall booking: {str(e)}"}, 500

class VendorStallDetailResource(Resource):
    @jwt_required()
    def get(self, booking_id):
        """Get a specific stall booking by ID."""
        current_user_id = get_jwt_identity()

        # Verify user is a vendor
        user = User.query.get(current_user_id)
        if not user or user.role != 'Vendor':
            return {"message": "Access denied. Vendor role required."}, 403

        booking = StallBooking.query.filter_by(id=booking_id, vendor_id=current_user_id).first()
        if not booking:
            return {"message": "Stall booking not found or access denied."}, 404

        return jsonify(stall_booking_schema.dump(booking)), 200

    @jwt_required()
    def put(self, booking_id):
        """Update a stall booking."""
        current_user_id = get_jwt_identity()

        # Verify user is a vendor
        user = User.query.get(current_user_id)
        if not user or user.role != 'Vendor':
            return {"message": "Access denied. Vendor role required."}, 403

        booking = StallBooking.query.filter_by(id=booking_id, vendor_id=current_user_id).first()
        if not booking:
            return {"message": "Stall booking not found or access denied."}, 404

        # Only allow updates if status is still pending
        if booking.status != 'Pending':
            return {"message": "Cannot update booking that is no longer pending."}, 400

        data = request.get_json()

        try:
            # Update fields if provided
            if 'stall_type' in data:
                booking.stall_type = data['stall_type']
            if 'description' in data:
                booking.description = data['description']

            db.session.commit()

            return jsonify(stall_booking_schema.dump(booking)), 200

        except Exception as e:
            db.session.rollback()
            return {"message": f"Error updating stall booking: {str(e)}"}, 500

    @jwt_required()
    def delete(self, booking_id):
        """Cancel a stall booking."""
        current_user_id = get_jwt_identity()

        # Verify user is a vendor
        user = User.query.get(current_user_id)
        if not user or user.role != 'Vendor':
            return {"message": "Access denied. Vendor role required."}, 403

        booking = StallBooking.query.filter_by(id=booking_id, vendor_id=current_user_id).first()
        if not booking:
            return {"message": "Stall booking not found or access denied."}, 404

        # Only allow deletion if status is still pending
        if booking.status != 'Pending':
            return {"message": "Cannot cancel booking that is no longer pending."}, 400

        try:
            db.session.delete(booking)
            db.session.commit()
            return {"message": "Stall booking cancelled successfully."}, 200

        except Exception as e:
            db.session.rollback()
            return {"message": f"Error cancelling stall booking: {str(e)}"}, 500

# Register the resources with the API blueprint
api.add_resource(VendorStallListResource, '/stalls')
api.add_resource(VendorStallDetailResource, '/stalls/<int:booking_id>')