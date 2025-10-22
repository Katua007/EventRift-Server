from flask_restful import Resource
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app.app import api # Assuming you'll import api from the main app instance

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

def initialize_user_routes(api):
    api.add_resource(Login, '/login')
    api.add_resource(Protected, '/protected')
    # Add other user routes here