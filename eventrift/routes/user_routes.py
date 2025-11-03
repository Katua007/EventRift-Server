# Import Flask components for building web routes and handling requests
from flask import Blueprint, request, jsonify
# Import JWT functions for authentication and authorization
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
# Import the User model for database operations
from eventrift.models.user import User
# Import database instance
from eventrift.extensions import db

# RBAC (Role-Based Access Control) Helper - can be moved to separate utils file later
from functools import wraps

# Try to import email service for sending verification emails
try:
    from eventrift.utils.email_service import send_verification_email
except ImportError:
    # Fallback function if email service is not available
    def send_verification_email(*args):
        return True

# Decorator function to check if user has required role
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Get claims from JWT token
            claims = get_jwt()
            # Check if user's role matches required role
            if claims.get('role') == role:
                return fn(*args, **kwargs)
            # Return forbidden error if role doesn't match
            return {'message': f'Role {role} required'}, 403
        return decorator
    return wrapper

# Create blueprint for user-related routes
user_bp = Blueprint('user', __name__)

# Route for user login - accepts POST requests with user credentials
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
    # Get login data from request body
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Find user in database by email
    user = User.query.filter_by(email=email).first()

    # Check if user exists and password is correct
    if user and user.check_password(password):
        # Create JWT token with user ID and role information
        access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
        # Return token and role
        return {'access_token': access_token, 'role': user.role}, 200

    # Return error for invalid credentials
    return {'message': 'Invalid email or password'}, 401

# Example protected route that requires authentication
@user_bp.route('/protected', methods=['GET'])
@jwt_required()  # Requires valid JWT token
def protected():
    # Example of getting user data from the JWT token payload
    try:
        # Get the user identity from the JWT token
        current_user_id = get_jwt_identity()
        # Convert to int if it's a string (JWT identity might be string)
        if isinstance(current_user_id, str):
            try:
                current_user_id = int(current_user_id)
            except ValueError:
                # If conversion fails, try to find user by email instead
                user = User.query.filter_by(email=current_user_id).first()
                if user:
                    current_user_id = user.id
                else:
                    return {'message': 'User not found'}, 404

        # Return welcome message with user ID
        return {'message': f'Welcome, User {current_user_id}. This route is protected!'}, 200
    except Exception as e:
        print(f"Error in protected route: {e}")
        return {'message': 'Internal server error'}, 500

# Route for user registration - creates new user accounts
@user_bp.route('/users', methods=['POST'])
def register():
    # Public signup endpoint - anyone can create an account
    data = request.get_json()

    # NOTE: Add Marshmallow validation here later for better input validation

    # Check if email is already registered
    if User.query.filter_by(email=data.get('email')).first():
         return {'message': 'Email already registered'}, 409

    try:
        # Create new user with default role of 'Goer' unless specified
        new_user = User(
            username=data.get('username'),
            email=data.get('email'),
            role=data.get('role', 'Goer'),  # Default role for regular users
            password_hash=data.get('password')  # The User model setter handles password hashing
        )
        # Add user to database session
        db.session.add(new_user)
        # Save changes to database
        db.session.commit()

        # --- NEW EMAIL INTEGRATION ---
        # Generate verification token for email confirmation
        token = new_user.verification_token
        # Send verification email
        email_sent = send_verification_email(new_user.email, token)

        if email_sent:
            # Email sent successfully
            return {'message': 'User registered. Please check your email for verification link.'}, 201
        else:
            # User created but email failed (not a critical error)
            return {'message': 'User registered, but verification email failed to send. Try again later.'}, 202

    except Exception as e:
        # Rollback database changes if error occurs
        db.session.rollback()
        return {'message': f'Error during registration: {str(e)}'}, 500

# Route to get all users - admin only access
@user_bp.route('/users', methods=['GET'])
@jwt_required()  # Requires authentication
@role_required('Admin')  # Only admins can access this - example of RBAC protection
def get_users():
    # Admin-only endpoint: Get list of all users in the system
    try:
        # Query all users from database
        users = User.query.all()
        # NOTE: Use Marshmallow Schema for serialization here later for better data formatting
        # Return basic user info for each user
        return [{'id': u.id, 'username': u.username, 'role': u.role} for u in users], 200
    except Exception as e:
        print(f"Error in get_users: {e}")
        return {'message': 'Internal server error'}, 500
