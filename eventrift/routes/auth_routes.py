from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint for frontend"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Mock authentication for now
        if email and password:
            access_token = create_access_token(
                identity=email,
                additional_claims={'role': 'user'}
            )
            return {
                'success': True,
                'access_token': access_token,
                'user': {
                    'email': email,
                    'role': 'user'
                }
            }, 200

        return {'success': False, 'message': 'Invalid credentials'}, 401

    except Exception as e:
        return {'success': False, 'message': str(e)}, 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register endpoint for frontend"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        if email and password and name:
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': {
                    'email': email,
                    'name': name,
                    'role': 'user'
                }
            }, 201

        return {'success': False, 'message': 'Missing required fields'}, 400

    except Exception as e:
        return {'success': False, 'message': str(e)}, 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Get current user info"""
    try:
        current_user = get_jwt_identity()
        return {
            'success': True,
            'user': {
                'email': current_user,
                'role': 'user'
            }
        }, 200
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500
