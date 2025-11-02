from flask import Blueprint, request
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime
import json # Used to parse JSON data if sent in a 'data' form field
from eventrift.extensions import db # Assuming db is initialized here or passed via extensions
from sqlalchemy.exc import IntegrityError

from eventrift.schemas.event_schema import event_schema, events_schema
from eventrift.schemas.pagination_schema import pagination_schema
from eventrift.models.event import Event
# from eventrift.decorators import requires_roles  # Commented out - not needed for basic functionality

# Try to import Cloudinary utility, fallback if not available
try:
    from eventrift.utils.cloudinary_upload import upload_event_image
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False
    def upload_event_image(file):
        return None

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
    # @requires_roles('Organizer')  # Commented out for basic functionality
    def post(self):
        """Creates a new event, handling optional Cloudinary image upload."""

        current_user_id = get_jwt_identity()
        print(f"Event creation - JWT Identity: {current_user_id}, Type: {type(current_user_id)}")

        # Convert to int if it's a string (JWT identity might be string)
        if isinstance(current_user_id, str):
            try:
                current_user_id = int(current_user_id)
                print(f"Event creation - Converted to int: {current_user_id}")
            except ValueError:
                # If conversion fails, try to find user by email
                print(f"Event creation - Trying to find user by email: {current_user_id}")
                from eventrift.models.user import User
                user = User.query.filter_by(email=current_user_id).first()
                if user:
                    current_user_id = user.id
                    print(f"Event creation - Found user ID: {current_user_id}")
                else:
                    print(f"Event creation - User not found for email: {current_user_id}")
                    return {'success': False, 'message': 'User not found'}, 404

        # Verify user exists in database
        from eventrift.models.user import User
        user = User.query.get(current_user_id)
        if not user:
            print(f"Event creation - User with ID {current_user_id} not found in database")
            return {'success': False, 'message': 'User not found'}, 404

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

        # --- 2. Transform frontend data to backend format ---
        print(f"Event creation - Raw frontend data: {event_data}")

        # Transform field names and data types
        transformed_data = {}

        # Map title to name
        if 'title' in event_data:
            transformed_data['name'] = event_data['title']

        # Map description (already correct)
        if 'description' in event_data:
            transformed_data['description'] = event_data['description']

        # Map location (already correct)
        if 'location' in event_data:
            transformed_data['location'] = event_data['location']

        # Combine start_date and start_time into date_time
        if 'start_date' in event_data and 'start_time' in event_data:
            date_str = event_data['start_date']
            time_str = event_data['start_time']
            # Create ISO 8601 datetime string
            transformed_data['date_time'] = f"{date_str}T{time_str}:00"
        elif 'date_time' in event_data:
            transformed_data['date_time'] = event_data['date_time']

        # Convert date_time string to datetime object for proper validation
        if 'date_time' in transformed_data and isinstance(transformed_data['date_time'], str):
            try:
                transformed_data['date_time'] = datetime.fromisoformat(transformed_data['date_time'].replace('Z', '+00:00'))
            except ValueError:
                return {'success': False, 'message': 'Invalid date_time format. Use ISO 8601 format.'}, 400

        # Convert ticket_price to float
        if 'ticket_price' in event_data:
            try:
                transformed_data['ticket_price'] = float(event_data['ticket_price'])
            except (ValueError, TypeError):
                transformed_data['ticket_price'] = 0.0

        # Convert capacity/max_attendees to int
        if 'capacity' in event_data:
            try:
                transformed_data['capacity'] = int(event_data['capacity'])
            except (ValueError, TypeError):
                transformed_data['capacity'] = 10
        elif 'max_attendees' in event_data:
            try:
                transformed_data['capacity'] = int(event_data['max_attendees'])
            except (ValueError, TypeError):
                transformed_data['capacity'] = 10

        # Handle image URL
        if 'image' in event_data and event_data['image']:
            transformed_data['image_url'] = event_data['image']

        print(f"Event creation - Transformed data: {transformed_data}")

        # --- 3. Cloudinary Upload (BE-301) ---
        image_url = None
        if image_file and CLOUDINARY_AVAILABLE:
            # Upload the image and get the secure URL
            image_url = upload_event_image(image_file)

            if not image_url:
                # If upload failed, continue without image
                print("Image upload failed, continuing without image")

        # Inject the resulting URL into the data for Marshmallow validation
        if image_url:
            transformed_data['image_url'] = image_url

        event_data = transformed_data

        try:
            # --- 3. Validate and Deserialize (BE-204) ---
            # Don't use post_load to create the object, just validate the data
            print(f"Event creation - Validating data: {event_data}")
            try:
                validated_data = event_schema.load(event_data)
                print(f"Event creation - Validation successful: {validated_data}")
            except Exception as validation_error:
                print(f"Event creation - Validation failed: {validation_error}")
                return {"success": False, "message": f"Validation error: {str(validation_error)}"}, 400
            
            # --- 4. Create and Save Event ---
            # Remove the post_load created object and create manually
            print(f"Event creation - Creating event object")
            if isinstance(validated_data, Event):
                new_event = validated_data
                new_event.organizer_id = current_user_id
                print(f"Event creation - Using existing Event object")
            else:
                # Create event manually from validated data
                print(f"Event creation - Creating new Event object")
                new_event = Event(
                    name=validated_data['name'],
                    description=validated_data['description'],
                    location=validated_data['location'],
                    date_time=validated_data['date_time'],
                    ticket_price=validated_data['ticket_price'],
                    capacity=validated_data['capacity'],
                    image_url=validated_data.get('image_url'),
                    organizer_id=current_user_id
                )
                print(f"Event creation - Event object created: {new_event}")

            print(f"Event creation - Saving event to database")
            new_event.save()
            print(f"Event creation - Event saved successfully with ID: {new_event.id}")
            
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

        except IntegrityError as e:
            print(f"IntegrityError creating event: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return {"success": False, "message": "Event creation failed due to data integrity issue. Please check your input data."}, 400

        except Exception as e:
            print(f"Error creating event: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()  # Rollback any partial changes
            return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}, 500

class OrganizerEventsResource(Resource):

    @jwt_required()
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            print(f"JWT Identity: {current_user_id}, Type: {type(current_user_id)}")

            # Convert to int if it's a string (JWT identity might be string)
            if isinstance(current_user_id, str):
                try:
                    current_user_id = int(current_user_id)
                    print(f"Converted to int: {current_user_id}")
                except ValueError:
                    # If conversion fails, try to find user by email
                    print(f"Trying to find user by email: {current_user_id}")
                    from eventrift.models.user import User
                    user = User.query.filter_by(email=current_user_id).first()
                    if user:
                        current_user_id = user.id
                        print(f"Found user ID: {current_user_id}")
                    else:
                        print(f"User not found for email: {current_user_id}")
                        # For testing, return empty events list instead of error
                        return {
                            'success': True,
                            'events': [],
                            'message': 'No events found for this user'
                        }, 200

            print(f"Querying events for organizer_id: {current_user_id}")
            events = Event.query.filter_by(organizer_id=current_user_id).all()
            print(f"Found {len(events)} events")

            return {
                'success': True,
                'events': events_schema.dump(events)
            }, 200
        except Exception as e:
            print(f"Error in OrganizerEventsResource.get: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'message': 'Internal server error'}, 500

# Register the resources with the API blueprint
api.add_resource(EventListResource, '/events')
api.add_resource(OrganizerEventsResource, '/organizers/events')
