from flask_restful import Resource
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from eventrift.extensions import api, db

class AuthLogin(Resource):
    def post(self):
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

class AuthRegister(Resource):
    def post(self):
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

class AuthMe(Resource):
    @jwt_required()
    def get(self):
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

def initialize_auth_routes(api):
    api.add_resource(AuthLogin, '/auth/login')
    api.add_resource(AuthRegister, '/auth/register')
    api.add_resource(AuthMe, '/auth/profile')