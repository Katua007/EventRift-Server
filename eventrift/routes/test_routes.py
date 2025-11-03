from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from eventrift.extensions import db
from eventrift.models.user import User
from eventrift.models.event import Event
from eventrift.models.vendor_service import VendorService
from eventrift.models.ticket_attendance import Ticket, Attendance
from eventrift.models.stall_booking import StallBooking, StallPayment, StallType
from datetime import datetime, timedelta

test_bp = Blueprint('test', __name__)

@test_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {
        'success': True,
        'message': 'EventRift Server is running',
        'timestamp': datetime.utcnow().isoformat()
    }, 200

@test_bp.route('/setup-test-data', methods=['POST'])
def setup_test_data():
    """Setup test data for all user roles"""
    try:
        # Create test users for each role
        test_users = [
            {'email': 'goer@test.com', 'username': 'Test Goer', 'role': 'Goer', 'password': 'password123'},
            {'email': 'organizer@test.com', 'username': 'Test Organizer', 'role': 'Organizer', 'password': 'password123'},
            {'email': 'vendor@test.com', 'username': 'Test Vendor', 'role': 'Vendor', 'password': 'password123'},
            {'email': 'admin@test.com', 'username': 'Test Admin', 'role': 'Admin', 'password': 'password123'}
        ]
        
        created_users = {}
        for user_data in test_users:
            # Check if user already exists
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if not existing_user:
                new_user = User(
                    email=user_data['email'],
                    username=user_data['username'],
                    role=user_data['role'],
                    password_hash=user_data['password']
                )
                db.session.add(new_user)
                db.session.flush()
                created_users[user_data['role']] = new_user
            else:
                created_users[user_data['role']] = existing_user
        
        # Create test events
        if 'Organizer' in created_users:
            organizer = created_users['Organizer']
            test_events = [
                {
                    'name': 'Tech Conference 2024',
                    'description': 'Annual technology conference with latest trends',
                    'location': 'Nairobi Convention Center',
                    'date_time': datetime.utcnow() + timedelta(days=30),
                    'ticket_price': 2500.00,
                    'capacity': 500,
                    'is_published': True,
                    'organizer_id': organizer.id
                },
                {
                    'name': 'Music Festival',
                    'description': 'Live music performances from top artists',
                    'location': 'Uhuru Park',
                    'date_time': datetime.utcnow() + timedelta(days=45),
                    'ticket_price': 1500.00,
                    'capacity': 1000,
                    'is_published': True,
                    'organizer_id': organizer.id
                }
            ]
            
            for event_data in test_events:
                existing_event = Event.query.filter_by(name=event_data['name']).first()
                if not existing_event:
                    new_event = Event(**event_data)
                    db.session.add(new_event)
        
        # Create test vendor services
        if 'Vendor' in created_users:
            vendor = created_users['Vendor']
            test_services = [
                {
                    'vendor_id': vendor.id,
                    'service_name': 'Professional Photography',
                    'service_description': 'High-quality event photography services',
                    'service_category': 'Photography',
                    'pricing_model': 'per_hour',
                    'base_price': 5000.00,
                    'contact_phone': '+254700000001',
                    'contact_email': 'photo@vendor.com',
                    'service_location': 'Nairobi'
                },
                {
                    'vendor_id': vendor.id,
                    'service_name': 'Catering Services',
                    'service_description': 'Delicious meals for all event types',
                    'service_category': 'Catering',
                    'pricing_model': 'per_person',
                    'base_price': 800.00,
                    'contact_phone': '+254700000002',
                    'contact_email': 'catering@vendor.com',
                    'service_location': 'Nairobi'
                }
            ]
            
            for service_data in test_services:
                existing_service = VendorService.query.filter_by(
                    vendor_id=service_data['vendor_id'],
                    service_name=service_data['service_name']
                ).first()
                if not existing_service:
                    new_service = VendorService(**service_data)
                    db.session.add(new_service)
        
        # Create test stall types
        test_stall_types = [
            {'name': 'Food Stall', 'price': 15000.00, 'size': '3m x 3m', 'description': 'Perfect for food vendors'},
            {'name': 'Merchandise Stall', 'price': 10000.00, 'size': '2m x 2m', 'description': 'Ideal for selling merchandise'},
            {'name': 'Premium Stall', 'price': 25000.00, 'size': '4m x 4m', 'description': 'Large premium space'}
        ]
        
        for stall_data in test_stall_types:
            existing_stall = StallType.query.filter_by(name=stall_data['name']).first()
            if not existing_stall:
                new_stall_type = StallType(**stall_data)
                db.session.add(new_stall_type)
        
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Test data created successfully',
            'users_created': list(created_users.keys())
        }, 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating test data: {e}")
        return {'success': False, 'message': f'Failed to create test data: {str(e)}'}, 500

@test_bp.route('/endpoints', methods=['GET'])
def list_endpoints():
    """List all available API endpoints"""
    endpoints = {
        'Authentication': {
            'POST /auth/login': 'User login',
            'POST /auth/register': 'User registration',
            'GET /auth/profile': 'Get user profile (requires auth)',
            'POST /auth/logout': 'User logout'
        },
        'Dashboard': {
            'GET /api/dashboard': 'Get role-specific dashboard data (requires auth)',
            'GET /api/profile': 'Get user profile (requires auth)',
            'PUT /api/profile': 'Update user profile (requires auth)'
        },
        'Events': {
            'GET /api/events': 'List all public events',
            'POST /api/events': 'Create new event (Organizer only)',
            'GET /api/organizers/events': 'Get organizer\'s events (requires auth)'
        },
        'Vendor Services': {
            'GET /vendors/services': 'Get vendor services (requires auth)',
            'POST /vendors/services': 'Create vendor service (Vendor only)',
            'PUT /vendors/services/<id>': 'Update service status (Admin only)'
        },
        'Tickets': {
            'GET /api/tickets/user': 'Get user tickets (requires auth)',
            'GET /api/tickets/<uuid>': 'Get specific ticket (requires auth)',
            'POST /api/tickets/checkin': 'Check in ticket (Organizer/Staff only)'
        },
        'Stalls': {
            'GET /api/stalls/': 'Get vendor stall bookings (requires auth)',
            'POST /api/stalls/': 'Create stall booking (Vendor only)',
            'GET /api/stalls/types/<event_id>': 'Get available stall types'
        },
        'Data Retrieval': {
            'GET /api/data/organizer': 'Get organizer data (requires auth)',
            'GET /api/data/vendor': 'Get vendor data (requires auth)',
            'GET /api/data/goer': 'Get goer data (requires auth)',
            'GET /api/data/system-overview': 'Get system overview (Admin only)'
        },
        'Testing': {
            'GET /api/test/health': 'Health check',
            'POST /api/test/setup-test-data': 'Setup test data',
            'GET /api/test/endpoints': 'List all endpoints'
        }
    }
    
    return {
        'success': True,
        'endpoints': endpoints,
        'base_url': request.host_url.rstrip('/')
    }, 200

@test_bp.route('/verify-roles', methods=['GET'])
@jwt_required()
def verify_roles():
    """Verify user role and permissions"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Convert to int if it's a string
        if isinstance(current_user_id, str):
            try:
                current_user_id = int(current_user_id)
            except ValueError:
                user = User.query.filter_by(email=current_user_id).first()
                if user:
                    current_user_id = user.id
                else:
                    return {'success': False, 'message': 'User not found'}, 404
        
        user = User.query.get(current_user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}, 404
        
        role_permissions = {
            'Goer': ['view_events', 'buy_tickets', 'view_own_tickets'],
            'Organizer': ['create_events', 'manage_own_events', 'check_in_tickets'],
            'Vendor': ['create_services', 'book_stalls', 'manage_own_services'],
            'Admin': ['manage_all_users', 'approve_services', 'system_overview']
        }
        
        return {
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role
            },
            'jwt_claims': claims,
            'permissions': role_permissions.get(user.role, [])
        }, 200
        
    except Exception as e:
        print(f"Error verifying roles: {e}")
        return {'success': False, 'message': 'Internal server error'}, 500