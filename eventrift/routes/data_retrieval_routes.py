from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from eventrift.extensions import db
from eventrift.models.user import User
from eventrift.models.event import Event
from eventrift.models.vendor_service import VendorService
from eventrift.models.payment import Payment
from eventrift.models.ticket_attendance import Ticket, Attendance
from sqlalchemy.orm import joinedload
from sqlalchemy import desc

# Create a Blueprint for data retrieval routes
data_retrieval_bp = Blueprint('data_retrieval_bp', __name__)
api = Api(data_retrieval_bp)

class OrganizerDataResource(Resource):
    @jwt_required()
    def get(self):
        """Retrieve all data related to an organizer's activities."""
        current_user_id = get_jwt_identity()
        
        # Get organizer's events
        events = Event.query.filter_by(organizer_id=current_user_id).all()
        
        # Get payments and tickets for organizer's events
        event_ids = [event.id for event in events]
        payments = Payment.query.filter(Payment.event_id.in_(event_ids)).all() if event_ids else []
        tickets = Ticket.query.filter(Ticket.event_id.in_(event_ids)).all() if event_ids else []
        
        # Compile data
        events_data = []
        for event in events:
            event_payments = [p for p in payments if p.event_id == event.id]
            event_tickets = [t for t in tickets if t.event_id == event.id]
            
            events_data.append({
                'id': event.id,
                'name': event.name,
                'description': event.description,
                'location': event.location,
                'date_time': event.date_time.isoformat() if event.date_time else None,
                'ticket_price': float(event.ticket_price) if event.ticket_price else 0,
                'capacity': event.capacity,
                'is_published': event.is_published,
                'created_at': event.created_at.isoformat() if event.created_at else None,
                'total_payments': len(event_payments),
                'total_revenue': sum(p.amount for p in event_payments if p.status == 'PAID'),
                'tickets_sold': len([t for t in event_tickets if t.status == 'PAID']),
                'tickets_checked_in': len([t for t in event_tickets if t.attendance and t.attendance.is_checked_in])
            })
        
        return {
            'success': True,
            'organizer_id': current_user_id,
            'total_events': len(events),
            'events': events_data
        }, 200

class VendorDataResource(Resource):
    @jwt_required()
    def get(self):
        """Retrieve all data related to a vendor's activities."""
        current_user_id = get_jwt_identity()
        
        # Get vendor's services
        services = VendorService.query.filter_by(vendor_id=current_user_id).all()
        
        services_data = []
        for service in services:
            services_data.append({
                'id': service.id,
                'service_name': service.service_name,
                'service_description': service.service_description,
                'service_category': service.service_category,
                'pricing_model': service.pricing_model,
                'base_price': service.base_price,
                'availability_status': service.availability_status,
                'license_status': service.license_status,
                'contact_phone': service.contact_phone,
                'contact_email': service.contact_email,
                'service_location': service.service_location,
                'created_at': service.created_at.isoformat() if service.created_at else None,
                'updated_at': service.updated_at.isoformat() if service.updated_at else None
            })
        
        return {
            'success': True,
            'vendor_id': current_user_id,
            'total_services': len(services),
            'services': services_data
        }, 200

class GoerDataResource(Resource):
    @jwt_required()
    def get(self):
        """Retrieve all data related to a goer's activities."""
        current_user_id = get_jwt_identity()
        
        # Get goer's payments and tickets
        payments = Payment.query.filter_by(user_id=current_user_id).options(
            joinedload(Payment.event)
        ).all()
        
        tickets = Ticket.query.filter_by(user_id=current_user_id).options(
            joinedload(Ticket.event),
            joinedload(Ticket.attendance)
        ).all()
        
        payments_data = []
        for payment in payments:
            payments_data.append({
                'id': payment.id,
                'event_name': payment.event.name if payment.event else 'Unknown Event',
                'amount': payment.amount,
                'quantity': payment.quantity,
                'status': payment.status,
                'phone_number': payment.phone_number,
                'mpesa_receipt_number': payment.mpesa_receipt_number,
                'transaction_date': payment.transaction_date.isoformat() if payment.transaction_date else None,
                'created_at': payment.created_at.isoformat() if payment.created_at else None
            })
        
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                'id': ticket.id,
                'uuid': ticket.uuid,
                'event_name': ticket.event.name if ticket.event else 'Unknown Event',
                'status': ticket.status,
                'ticket_type': ticket.ticket_type,
                'is_checked_in': ticket.attendance.is_checked_in if ticket.attendance else False,
                'checked_in_at': ticket.attendance.checked_in_at.isoformat() if ticket.attendance and ticket.attendance.checked_in_at else None,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None
            })
        
        return {
            'success': True,
            'user_id': current_user_id,
            'total_payments': len(payments),
            'total_tickets': len(tickets),
            'payments': payments_data,
            'tickets': tickets_data
        }, 200

class SystemOverviewResource(Resource):
    @jwt_required()
    def get(self):
        """Get system-wide overview of all captured data (Admin only)."""
        claims = get_jwt()
        if claims.get('role') != 'Admin':
            return {'success': False, 'message': 'Admin access required'}, 403
        
        # Get counts of all major entities
        total_users = User.query.count()
        total_events = Event.query.count()
        total_services = VendorService.query.count()
        total_payments = Payment.query.count()
        total_tickets = Ticket.query.count()
        
        # Get recent activities
        recent_events = Event.query.order_by(desc(Event.created_at)).limit(5).all()
        recent_services = VendorService.query.order_by(desc(VendorService.created_at)).limit(5).all()
        recent_payments = Payment.query.order_by(desc(Payment.created_at)).limit(5).all()
        
        return {
            'success': True,
            'system_overview': {
                'total_users': total_users,
                'total_events': total_events,
                'total_services': total_services,
                'total_payments': total_payments,
                'total_tickets': total_tickets,
                'recent_events': [{'id': e.id, 'name': e.name, 'created_at': e.created_at.isoformat()} for e in recent_events],
                'recent_services': [{'id': s.id, 'name': s.service_name, 'created_at': s.created_at.isoformat()} for s in recent_services],
                'recent_payments': [{'id': p.id, 'amount': p.amount, 'status': p.status, 'created_at': p.created_at.isoformat()} for p in recent_payments]
            }
        }, 200

# Register the resources with the API blueprint
api.add_resource(OrganizerDataResource, '/organizer')
api.add_resource(VendorDataResource, '/vendor')
api.add_resource(GoerDataResource, '/goer')
api.add_resource(SystemOverviewResource, '/system-overview')