from flask_restful import Resource
from flask import request
from app.models.vendor_service import VendorService
from app.models import db
from app.schemas.vendor_service_schema import vendor_service_schema, vendor_services_schema
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.routes.user_routes import role_required

class VendorServiceListResource(Resource):
    @jwt_required()
    @role_required('Vendor')
    def post(self):
        """Vendor-only: Register a new service (FE-304 submission)."""
        data = request.get_json()
        
        # Ensure the vendor_id in the payload matches the token identity
        if data.get('vendor_id') != get_jwt_identity():
            return {'message': 'Unauthorized vendor ID'}, 403

        try:
            # Note: licensing_document_url will likely come from a prior Cloudinary upload
            validated_data = vendor_service_schema.load(data)
            
            new_service = VendorService(**validated_data)
            db.session.add(new_service)
            db.session.commit()
            return vendor_service_schema.dump(new_service), 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error registering service: {str(e)}'}, 400
            
    @jwt_required()
    def get(self):
        """Get all services for the logged-in user (Vendor or Admin)."""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        if claims.get('role') == 'Admin':
            services = VendorService.query.all()
        else: # Vendor
            services = VendorService.query.filter_by(vendor_id=current_user_id).all()
            
        return vendor_services_schema.dump(services), 200

class VendorServiceResource(Resource):
    @jwt_required()
    @role_required('Admin')
    def put(self, service_id):
        """Admin-only: Update license status."""
        data = request.get_json()
        service = VendorService.query.get_or_404(service_id)

        if 'license_status' in data:
            # Only allow specific statuses
            if data['license_status'] in ['Verified', 'Suspended']:
                service.license_status = data['license_status']
                db.session.commit()
                return vendor_service_schema.dump(service), 200
            else:
                return {'message': 'Invalid license status value.'}, 400
        
        return {'message': 'No valid fields provided for update.'}, 400

def initialize_vendor_routes(api):
    api.add_resource(VendorServiceListResource, '/vendor/services')
    api.add_resource(VendorServiceResource, '/vendor/services/<int:service_id>')