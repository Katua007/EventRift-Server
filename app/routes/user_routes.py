from flask_restful import Resource
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app.app import api # Assuming you'll import api from the main app instance

# RBAC Helper (Can be moved to a separate utils/decorators file later)
from functools import wraps
from flask_jwt_extended import get_jwt
from app.models.user import User
from app.app import db # Import db instance
from app.utils.email_service import send_verification_email # NEW IMPORT

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

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # Create a token with user ID and role for RBAC
            access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
            return {'message': 'Login successful', 'access_token': access_token, 'user_role': user.role}, 200
        
        return {'message': 'Invalid credentials'}, 401

class Protected(Resource):
    @jwt_required()
    def get(self):
        # Example of getting user data from the token payload
        current_user_id = get_jwt_identity()
        return {'message': f'Welcome, User {current_user_id}. This route is protected!'}, 200


class UserListResource(Resource):
    def post(self):
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

            return {'message': 'User registered successfully'}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error during registration: {str(e)}'}, 500

    @jwt_required()
    @role_required('Admin') # Example of RBAC protection (Admin-only list)
    def get(self):
        # Admin-only: Get all users
        users = User.query.all()
        # NOTE: Use Marshmallow Schema for serialization here later
        return [{'id': u.id, 'username': u.username, 'role': u.role} for u in users], 200
    
def initialize_user_routes(api):
    api.add_resource(Login, '/login')
    api.add_resource(Protected, '/protected')
    # Add other user routes here
    api.add_resource(UserListResource, '/users')
    # api.add_resource(UserResource, '/users/<int:user_id>') # Add later