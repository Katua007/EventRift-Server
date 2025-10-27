from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from eventrift.extensions import api

class EventsAPI(Resource):
    def get(self):
        """Get all events - public endpoint"""
        # Mock events data
        events = [
            {
                'id': 1,
                'title': 'Tech Conference 2024',
                'description': 'Annual technology conference',
                'date': '2024-06-15',
                'location': 'Nairobi, Kenya',
                'price': 5000,
                'image': 'https://via.placeholder.com/400x300'
            },
            {
                'id': 2,
                'title': 'Music Festival',
                'description': 'Live music and entertainment',
                'date': '2024-07-20',
                'location': 'Mombasa, Kenya',
                'price': 3000,
                'image': 'https://via.placeholder.com/400x300'
            }
        ]
        
        return {
            'success': True,
            'events': events,
            'total': len(events)
        }, 200

    @jwt_required()
    def post(self):
        """Create new event - requires authentication"""
        try:
            data = request.get_json()
            current_user = get_jwt_identity()
            
            # Mock event creation
            new_event = {
                'id': 3,
                'title': data.get('title'),
                'description': data.get('description'),
                'date': data.get('date'),
                'location': data.get('location'),
                'price': data.get('price'),
                'organizer': current_user
            }
            
            return {
                'success': True,
                'message': 'Event created successfully',
                'event': new_event
            }, 201
            
        except Exception as e:
            return {'success': False, 'message': str(e)}, 500

class EventDetailAPI(Resource):
    def get(self, event_id):
        """Get single event by ID"""
        # Mock event detail
        event = {
            'id': event_id,
            'title': f'Event {event_id}',
            'description': 'Event description',
            'date': '2024-06-15',
            'location': 'Nairobi, Kenya',
            'price': 5000,
            'image': 'https://via.placeholder.com/400x300'
        }
        
        return {
            'success': True,
            'event': event
        }, 200

def initialize_events_api(api):
    api.add_resource(EventsAPI, '/api/events')
    api.add_resource(EventDetailAPI, '/api/events/<int:event_id>')