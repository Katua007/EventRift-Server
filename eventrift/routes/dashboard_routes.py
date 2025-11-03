from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from eventrift.extensions import db
from eventrift.models.user import User
from eventrift.models.event import Event
from eventrift.models.vendor_service import VendorService
from eventrift.models.ticket_attendance import Ticket, Attendance
from eventrift.models.stall_booking import StallBooking, StallPayment, StallType
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

def get_current_user():
    """Helper function to get current user with proper ID conversion"""
    current_user_id = get_jwt_identity()
    
    if isinstance(current_user_id, str):
        try:
            current_user_id = int(current_user_id)
        except ValueError:
            user = User.query.filter_by(email=current_user_id).first()
            if user:
                current_user_id = user.id
            else:
                return None, None
    
    user = User.query.get(current_user_id)
    return user, current_user_id

@dashboard_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get role-specific dashboard data"""
    user, user_id = get_current_user()
    if not user:
        return {'success': False, 'message': 'User not found'}, 404
    
    claims = get_jwt()
    role = claims.get('role', user.role)
    
    if role == 'Goer':
        return get_goer_dashboard(user_id)
    elif role == 'Organizer':
        return get_organizer_dashboard(user_id)
    elif role == 'Vendor':
        return get_vendor_dashboard(user_id)
    elif role == 'Admin':
        return get_admin_dashboard(user_id)
    else:
        return {'success': False, 'message': 'Invalid user role'}, 400

def get_goer_dashboard(user_id):
    """Dashboard data for event goers"""
    try:
        # Get user's tickets with event details
        tickets = Ticket.query.filter_by(user_id=user_id).options(
            joinedload(Ticket.event),
            joinedload(Ticket.attendance)
        ).order_by(desc(Ticket.created_at)).all()
        
        # Get upcoming events (public events)
        upcoming_events = Event.query.filter(
            Event.date_time > datetime.utcnow(),
            Event.status == 'Active',
            Event.is_published == True
        ).order_by(Event.date_time).limit(6).all()
        
        # Calculate statistics
        total_tickets = len(tickets)
        paid_tickets = len([t for t in tickets if t.status == 'PAID'])
        checked_in_tickets = len([t for t in tickets if t.attendance and t.attendance.is_checked_in])
        
        # Recent activity
        recent_tickets = tickets[:5]
        
        tickets_data = []
        for ticket in recent_tickets:
            tickets_data.append({
                'id': ticket.id,
                'uuid': ticket.uuid,
                'event_name': ticket.event.name if ticket.event else 'Unknown Event',
                'event_date': ticket.event.date_time.isoformat() if ticket.event and ticket.event.date_time else None,
                'event_location': ticket.event.location if ticket.event else None,
                'status': ticket.status,
                'ticket_type': ticket.ticket_type,
                'is_checked_in': ticket.attendance.is_checked_in if ticket.attendance else False,
                'checked_in_at': ticket.attendance.checked_in_at.isoformat() if ticket.attendance and ticket.attendance.checked_in_at else None,
                'created_at': ticket.created_at.isoformat(),
                'qr_code_data': ticket.encoded_qr_data
            })
        
        events_data = []
        for event in upcoming_events:
            events_data.append({
                'id': event.id,
                'name': event.name,
                'description': event.description,
                'location': event.location,
                'date_time': event.date_time.isoformat() if event.date_time else None,
                'ticket_price': float(event.ticket_price) if event.ticket_price else 0,
                'capacity': event.capacity,
                'image_url': event.image_url
            })
        
        return {
            'success': True,
            'role': 'Goer',
            'user_id': user_id,
            'stats': {
                'total_tickets': total_tickets,
                'paid_tickets': paid_tickets,
                'checked_in_tickets': checked_in_tickets,
                'upcoming_events': len(upcoming_events)
            },
            'recent_tickets': tickets_data,
            'upcoming_events': events_data
        }, 200
        
    except Exception as e:
        print(f"Error in goer dashboard: {e}")
        return {'success': False, 'message': 'Internal server error'}, 500

def get_organizer_dashboard(user_id):
    """Dashboard data for event organizers"""
    try:
        # Get organizer's events
        events = Event.query.filter_by(organizer_id=user_id).order_by(desc(Event.created_at)).all()
        
        # Get tickets for organizer's events
        event_ids = [event.id for event in events]
        tickets = []
        if event_ids:
            tickets = Ticket.query.filter(Ticket.event_id.in_(event_ids)).options(
                joinedload(Ticket.event),
                joinedload(Ticket.attendance)
            ).all()
        
        # Calculate statistics
        total_events = len(events)
        published_events = len([e for e in events if e.is_published])
        total_tickets_sold = len([t for t in tickets if t.status == 'PAID'])
        total_revenue = sum(float(e.ticket_price) * len([t for t in tickets if t.event_id == e.id and t.status == 'PAID']) for e in events)
        total_attendees = len([t for t in tickets if t.attendance and t.attendance.is_checked_in])
        
        # Recent events
        recent_events = events[:5]
        events_data = []
        for event in recent_events:
            event_tickets = [t for t in tickets if t.event_id == event.id]
            paid_tickets = [t for t in event_tickets if t.status == 'PAID']
            checked_in = [t for t in event_tickets if t.attendance and t.attendance.is_checked_in]
            
            events_data.append({
                'id': event.id,
                'name': event.name,
                'description': event.description,
                'location': event.location,
                'date_time': event.date_time.isoformat() if event.date_time else None,
                'ticket_price': float(event.ticket_price) if event.ticket_price else 0,
                'capacity': event.capacity,
                'is_published': event.is_published,
                'status': event.status,
                'image_url': event.image_url,
                'tickets_sold': len(paid_tickets),
                'revenue': len(paid_tickets) * float(event.ticket_price) if event.ticket_price else 0,
                'attendees_checked_in': len(checked_in),
                'created_at': event.created_at.isoformat()
            })
        
        # Upcoming events
        upcoming_events = [e for e in events if e.date_time and e.date_time > datetime.utcnow()][:3]
        upcoming_data = []
        for event in upcoming_events:
            event_tickets = [t for t in tickets if t.event_id == event.id and t.status == 'PAID']
            upcoming_data.append({
                'id': event.id,
                'name': event.name,
                'date_time': event.date_time.isoformat(),
                'location': event.location,
                'tickets_sold': len(event_tickets),
                'capacity': event.capacity
            })
        
        return {
            'success': True,
            'role': 'Organizer',
            'user_id': user_id,
            'stats': {
                'total_events': total_events,
                'published_events': published_events,
                'total_tickets_sold': total_tickets_sold,
                'total_revenue': total_revenue,
                'total_attendees': total_attendees
            },
            'recent_events': events_data,
            'upcoming_events': upcoming_data
        }, 200
        
    except Exception as e:
        print(f"Error in organizer dashboard: {e}")
        return {'success': False, 'message': 'Internal server error'}, 500

def get_vendor_dashboard(user_id):
    """Dashboard data for vendors"""
    try:
        # Get vendor's services
        services = VendorService.query.filter_by(vendor_id=user_id).order_by(desc(VendorService.created_at)).all()
        
        # Get vendor's stall bookings
        stall_bookings = StallBooking.query.filter_by(vendor_id=user_id).options(
            joinedload(StallBooking.payment),
            joinedload(StallBooking.stall_type)
        ).order_by(desc(StallBooking.created_at)).all()
        
        # Calculate statistics
        total_services = len(services)
        verified_services = len([s for s in services if s.license_status == 'Verified'])
        pending_services = len([s for s in services if s.license_status == 'Pending'])
        total_bookings = len(stall_bookings)
        confirmed_bookings = len([b for b in stall_bookings if b.status == 'CONFIRMED'])
        total_booking_revenue = sum(b.payment.amount for b in stall_bookings if b.payment and b.payment.status == 'PAID')
        
        # Recent services
        services_data = []
        for service in services[:5]:
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
                'created_at': service.created_at.isoformat()
            })
        
        # Recent bookings
        bookings_data = []
        for booking in stall_bookings[:5]:
            bookings_data.append({
                'id': booking.id,
                'event_id': booking.event_id,
                'business_name': booking.business_name,
                'products_offered': booking.products_offered,
                'status': booking.status,
                'stall_location': booking.stall_location,
                'stall_type_name': booking.stall_type.name if booking.stall_type else None,
                'stall_type_price': booking.stall_type.price if booking.stall_type else None,
                'payment_status': booking.payment.status if booking.payment else None,
                'payment_amount': booking.payment.amount if booking.payment else None,
                'created_at': booking.created_at.isoformat()
            })
        
        return {
            'success': True,
            'role': 'Vendor',
            'user_id': user_id,
            'stats': {
                'total_services': total_services,
                'verified_services': verified_services,
                'pending_services': pending_services,
                'total_bookings': total_bookings,
                'confirmed_bookings': confirmed_bookings,
                'total_booking_revenue': total_booking_revenue
            },
            'recent_services': services_data,
            'recent_bookings': bookings_data
        }, 200
        
    except Exception as e:
        print(f"Error in vendor dashboard: {e}")
        return {'success': False, 'message': 'Internal server error'}, 500

def get_admin_dashboard(user_id):
    """Dashboard data for administrators"""
    try:
        # Get system-wide statistics
        total_users = User.query.count()
        total_events = Event.query.count()
        total_services = VendorService.query.count()
        total_tickets = Ticket.query.count()
        total_bookings = StallBooking.query.count()
        
        # User breakdown by role
        user_roles = db.session.query(User.role, func.count(User.id)).group_by(User.role).all()
        role_stats = {role: count for role, count in user_roles}
        
        # Recent activities
        recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
        recent_events = Event.query.order_by(desc(Event.created_at)).limit(5).all()
        recent_services = VendorService.query.order_by(desc(VendorService.created_at)).limit(5).all()
        
        # Pending approvals
        pending_services = VendorService.query.filter_by(license_status='Pending').all()
        
        users_data = []
        for user in recent_users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        events_data = []
        for event in recent_events:
            events_data.append({
                'id': event.id,
                'name': event.name,
                'organizer_id': event.organizer_id,
                'location': event.location,
                'date_time': event.date_time.isoformat() if event.date_time else None,
                'is_published': event.is_published,
                'status': event.status,
                'created_at': event.created_at.isoformat()
            })
        
        services_data = []
        for service in recent_services:
            services_data.append({
                'id': service.id,
                'vendor_id': service.vendor_id,
                'service_name': service.service_name,
                'service_category': service.service_category,
                'license_status': service.license_status,
                'created_at': service.created_at.isoformat()
            })
        
        pending_data = []
        for service in pending_services:
            pending_data.append({
                'id': service.id,
                'vendor_id': service.vendor_id,
                'service_name': service.service_name,
                'service_category': service.service_category,
                'created_at': service.created_at.isoformat()
            })
        
        return {
            'success': True,
            'role': 'Admin',
            'user_id': user_id,
            'stats': {
                'total_users': total_users,
                'total_events': total_events,
                'total_services': total_services,
                'total_tickets': total_tickets,
                'total_bookings': total_bookings,
                'role_breakdown': role_stats
            },
            'recent_users': users_data,
            'recent_events': events_data,
            'recent_services': services_data,
            'pending_approvals': pending_data
        }, 200
        
    except Exception as e:
        print(f"Error in admin dashboard: {e}")
        return {'success': False, 'message': 'Internal server error'}, 500

@dashboard_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    user, user_id = get_current_user()
    if not user:
        return {'success': False, 'message': 'User not found'}, 404
    
    return {
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'license_number': user.license_number,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
    }, 200

@dashboard_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    user, user_id = get_current_user()
    if not user:
        return {'success': False, 'message': 'User not found'}, 404
    
    data = request.get_json()
    
    try:
        if 'username' in data:
            user.username = data['username']
        if 'license_number' in data and user.role == 'Vendor':
            user.license_number = data['license_number']
        
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'license_number': user.license_number
            }
        }, 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating profile: {e}")
        return {'success': False, 'message': 'Failed to update profile'}, 500