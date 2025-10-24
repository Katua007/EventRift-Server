from flask import Blueprint, request
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime
import json # Used to parse JSON data if sent in a 'data' form field
from app.extensions import db # Assuming db is initialized here or passed via extensions

from app.schemas.event_schema import event_schema, events_schema
from app.schemas.pagination_schema import pagination_schema
from app.models.event import Event
from app.decorators import requires_roles 
from app.utils.cloudinary_upload import upload_event_image # <-- Cloudinary Utility

# Create a Blueprint for event routes
events_bp = Blueprint('events_bp', __name__)
api = Api(events_bp)

class EventListResource(Resource):
    
    def get(self):
        """Public route: List all active events with pagination."""
        
        # 1. Get query parameters with defaults
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int) # Default 12 items per page

        # Ensure per_page is reasonable (e.g., max 50)
        if per_page > 50:
            per_page = 50

        # 2. Execute pagination query
        pagination = Event.query.filter_by(status='Active').paginate(
            page=page, 
            per_page=per_page, 
            error_out=False # Return empty page instead of 404 if out of bounds
        )

        events = pagination.items
        
        # 3. Create the serialized response structure
        response_data = {
            'events': events_schema.dump(events),
            'pagination': pagination_schema.dump(pagination)
        }
        
        return response_data, 200

    # BE-204 & BE-301: POST /api/events (Organizer Required)
    @jwt_required()
    @requires_roles('Organizer') 
    def post(self):
        """Creates a new event, handling optional Cloudinary image upload."""
        
        current_user_id = get_jwt_identity()

        # --- 1. Identify Data Source ---
        # request.files contains the uploaded image file (if any).
        # request.form contains non-file data for multipart/form-data requests.
        # request.get_json() contains data for application/json requests.
        
        image_file = request.files.get('image')
        event_data = {}
        
        # Priority 1: Check request.form (for multipart/form-data)
        if request.form:
            # Check if event details are sent as a JSON string in a 'data' field
            if 'data' in request.form:
                try:
                    event_data.update(json.loads(request.form['data']))
                except json.JSONDecodeError:
                    return {'message': 'Invalid JSON data provided in the form field.'}, 400
            else:
                 # If not in 'data', assume simple form fields hold event properties
                event_data.update(request.form)
                
        # Priority 2: Check JSON body (if no form data or file was uploaded)
        elif request.is_json:
            event_data.update(request.get_json()) 

        if not event_data:
            return {'message': 'No event data provided.'}, 400

        # --- 2. Cloudinary Upload (BE-301) ---
        image_url = None
        if image_file:
            # Upload the image and get the secure URL
            image_url = upload_event_image(image_file)
            
            if not image_url:
                # If upload failed, stop the process and notify the user
                return {"success": False, "message": "Image upload failed. Check Cloudinary settings or file format."}, 500
        
        # Inject the resulting URL into the data for Marshmallow validation
        event_data['image_url'] = image_url 

        try:
            # --- 3. Validate and Deserialize (BE-204) ---
            validated_data = event_schema.load(event_data)
            
            # --- 4. Create and Save Event ---
            new_event = Event(**validated_data)
            new_event.organizer_id = current_user_id 
            
            new_event.save() 
            
            # --- 5. Return Response ---
            result = event_schema.dump(new_event)
            return {
                "success": True, 
                "message": "Event created successfully.", 
                "event": result
            }, 201

        except ValidationError as err:
            # Database saving hasn't happened yet, so no cleanup needed.
            return {"success": False, "errors": err.messages}, 422
            
        except Exception as e:
            print(f"Error creating event: {e}")
            return {"success": False, "message": "An unexpected error occurred."}, 500

# Register the resource with the API blueprint
api.add_resource(EventListResource, '/events')
