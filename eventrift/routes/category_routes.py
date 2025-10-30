from flask_restful import Resource
from flask import request
from app.models.event_category import EventCategory
from app.models import db
from app.schemas.category_schema import category_schema, categories_schema
from flask_jwt_extended import jwt_required
from app.routes.user_routes import role_required

class CategoryListResource(Resource):
    def get(self):
        """Public: Get all event categories."""
        categories = EventCategory.query.all()
        return categories_schema.dump(categories), 200
    
    @jwt_required()
    @role_required('Admin')
    def post(self):
        """Admin-only: Create a new event category."""
        data = request.get_json()
        
        try:
            validated_data = category_schema.load(data)
            
            new_category = EventCategory(**validated_data)
            db.session.add(new_category)
            db.session.commit()
            return category_schema.dump(new_category), 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error creating category: {str(e)}'}, 400

class CategoryResource(Resource):
    def get(self, category_id):
        """Public: Get a specific category."""
        category = EventCategory.query.get_or_404(category_id)
        return category_schema.dump(category), 200
    
    @jwt_required()
    @role_required('Admin')
    def put(self, category_id):
        """Admin-only: Update a category."""
        category = EventCategory.query.get_or_404(category_id)
        data = request.get_json()
        
        try:
            validated_data = category_schema.load(data, partial=True)
            
            for key, value in validated_data.items():
                setattr(category, key, value)
            
            db.session.commit()
            return category_schema.dump(category), 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error updating category: {str(e)}'}, 400
    
    @jwt_required()
    @role_required('Admin')
    def delete(self, category_id):
        """Admin-only: Delete a category."""
        category = EventCategory.query.get_or_404(category_id)
        
        try:
            db.session.delete(category)
            db.session.commit()
            return {'message': 'Category deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error deleting category: {str(e)}'}, 400

def initialize_category_routes(api):
    api.add_resource(CategoryListResource, '/categories')
    api.add_resource(CategoryResource, '/categories/<int:category_id>')