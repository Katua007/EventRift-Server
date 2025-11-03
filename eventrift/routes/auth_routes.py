# Import Flask components for building web routes
from flask import Blueprint, request, jsonify
# Import JWT functions for authentication tokens
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Create a blueprint for authentication routes - this groups related routes together
auth_bp = Blueprint('auth', __name__)

# Route for user login - accepts POST requests with email and password
@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint for frontend - authenticates users and returns JWT token"""
    try:
        # Get the JSON data from the request body
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Simple mock authentication - in real app this would check database
        if email and password:
            # Create a JWT access token for the authenticated user
            access_token = create_access_token(
                identity=email,  # User's identity (email in this case)
                additional_claims={'role': 'user'}  # Extra info in the token
            )
            # Return success response with token and basic user info
            return {
                'success': True,
                'access_token': access_token,
                'user': {
                    'email': email,
                    'role': 'user'
                }
            }, 200

        # Return error if email or password missing
        return {'success': False, 'message': 'Invalid credentials'}, 401

    except Exception as e:
        # Return error if something goes wrong
        return {'success': False, 'message': str(e)}, 500

# Route for user registration - accepts POST requests to create new accounts
@auth_bp.route('/register', methods=['POST'])
def register():
    """Register endpoint for frontend - creates new user accounts"""
    try:
        # Get registration data from request body
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name') or data.get('username')

        # Check if all required fields are provided
        if email and password and name:
            # Return success response with user info (mock registration)
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': {
                    'email': email,
                    'name': name,
                    'role': 'user'
                }
            }, 201

        # Return error if required fields are missing
        return {'success': False, 'message': 'Missing required fields'}, 400

    except Exception as e:
        # Return error if something goes wrong during registration
        return {'success': False, 'message': str(e)}, 500

# Route for user logout - accepts POST requests to end user sessions
@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint for frontend - ends user authentication sessions"""
    try:
        print("Backend Auth: Logout request received")

        # For logout, we just return success since session cleanup is handled on frontend
        # In a real app, you might invalidate tokens or update session status
        print("Backend Auth: Logout successful")
        return {
            'success': True,
            'message': 'Logged out successfully'
        }, 200

    except Exception as e:
        print(f"Backend Auth: Logout error - {str(e)}")
        return {'success': False, 'message': str(e)}, 500

# Route to get current user's profile information - requires authentication
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()  # This decorator requires a valid JWT token
def profile():
    """Get current user info - returns profile data for authenticated users"""
    try:
        # Get the user identity from the JWT token
        current_user = get_jwt_identity()
        # Return user profile information
        return {
            'success': True,
            'user': {
                'email': current_user,
                'role': 'user'
            }
        }, 200
    except Exception as e:
        # Return error if something goes wrong
        return {'success': False, 'message': str(e)}, 500
