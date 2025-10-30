from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from eventrift.models.user import User
from eventrift.extensions import db

# RBAC Helper (Can be moved to a separate utils/decorators file later)
from functools import wraps

try:
    from eventrift.utils.email_service import send_verification_email
except ImportError:
    # Fallback for basic setup
    def send_verification_email(*args):
        return True

def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') == role:
                return fn(*args, **kwargs)
            return {'message': f'Role {role} required'}, 403
        return decorator
    return wrapper

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['POST'])
def login():
    """
    User Login Endpoint (Returns JWT Token)
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: organizer@example.com
            password:
              type: string
              example: password123
    responses:
      200:
        description: Login successful, returns access token.
        schema:
          type: object
          properties:
            access_token:
              type: string
            role:
              type: string
      401:
        description: Invalid credentials.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        # Create token with identity and claims (role)
        access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
        return {'access_token': access_token, 'role': user.role}, 200

    return {'message': 'Invalid email or password'}, 401

@user_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    # Example of getting user data from the token payload
    current_user_id = get_jwt_identity()
    return {'message': f'Welcome, User {current_user_id}. This route is protected!'}, 200

@user_bp.route('/users', methods=['POST'])
def register():
    # Public Signup (A-1)
    data = request.get_json()

    # NOTE: Add Marshmallow validation here later

    if User.query.filter_by(email=data.get('email')).first():
         return {'message': 'Email already registered'}, 409

    try:
        # Default role is Goer unless specified (for future Admin creation)
        new_user = User(
            username=data.get('username'),
            email=data.get('email'),
            role=data.get('role', 'Goer'),
            password_hash=data.get('password') # The setter handles hashing
        )
        db.session.add(new_user)
        db.session.commit()

        # --- NEW EMAIL INTEGRATION ---
        token = new_user.verification_token
        email_sent = send_verification_email(new_user.email, token)

        if email_sent:
            return {'message': 'User registered. Please check your email for verification link.'}, 201
        else:
            # User is created, but email failed to send (a soft error)
            return {'message': 'User registered, but verification email failed to send. Try again later.'}, 202

    except Exception as e:
        db.session.rollback()
        return {'message': f'Error during registration: {str(e)}'}, 500

@user_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required('Admin') # Example of RBAC protection (Admin-only list)
def get_users():
    # Admin-only: Get all users
    users = User.query.all()
    # NOTE: Use Marshmallow Schema for serialization here later
    return [{'id': u.id, 'username': u.username, 'role': u.role} for u in users], 200
