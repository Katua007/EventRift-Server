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

        if not email or not password:
            return {'success': False, 'message': 'Email and password required'}, 400

        # Try database authentication first, fallback to mock
        try:
            from eventrift.models.user import User
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                access_token = create_access_token(
                    identity=user.id,
                    additional_claims={'role': user.role}
                )
                return {
                    'success': True,
                    'access_token': access_token,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'role': user.role
                    }
                }, 200
        except ImportError:
            # Fallback to mock authentication
            username = email.split('@')[0] if '@' in email else email
            access_token = create_access_token(
                identity=email,
                additional_claims={'role': 'Goer'}
            )
            return {
                'success': True,
                'access_token': access_token,
                'user': {
                    'id': hash(email) % 10000,
                    'email': email,
                    'username': username,
                    'role': 'Goer'
                }
            }, 200

        return {'success': False, 'message': 'Invalid email or password'}, 401

    except Exception as e:
        return {'success': False, 'message': 'Internal server error'}, 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register endpoint for frontend"""
    try:
        from eventrift.models.user import User
        from eventrift.extensions import db
        
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        username = data.get('username') or data.get('name')
        role = data.get('role', 'Goer')

        if not email or not password or not username:
            return {'success': False, 'message': 'Email, password, and username are required'}, 400

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return {'success': False, 'message': 'Email already registered'}, 409

        # Create new user
        new_user = User(
            email=email,
            username=username,
            role=role,
            password_hash=password  # This will be hashed by the setter
        )
        
        db.session.add(new_user)
        db.session.commit()

        # Create access token
        access_token = create_access_token(
            identity=new_user.id,
            additional_claims={'role': new_user.role}
        )

        return {
            'success': True,
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'username': new_user.username,
                'role': new_user.role
            }
        }, 201

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return {'success': False, 'message': 'Registration failed'}, 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint for frontend"""
    try:
        print("🔐 Backend Auth: Logout request received")

        # For logout, we just return success since session cleanup is handled on frontend
        print("🔐 Backend Auth: Logout successful")
        return {
            'success': True,
            'message': 'Logged out successfully'
        }, 200

    except Exception as e:
        print(f"🔐 Backend Auth: Logout error - {str(e)}")
        return {'success': False, 'message': str(e)}, 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Get current user info"""
    try:
        from eventrift.models.user import User
        
        current_user_id = get_jwt_identity()
        
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
        
        return {
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role,
                'license_number': user.license_number
            }
        }, 200
    except Exception as e:
        print(f"Profile error: {e}")
        return {'success': False, 'message': 'Internal server error'}, 500
