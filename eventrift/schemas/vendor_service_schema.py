# Import Marshmallow for data validation and serialization
from marshmallow import Schema, fields, validate

# Schema for validating and serializing VendorService data
class VendorServiceSchema(Schema):
    # ID is read-only (only shown when returning data, not required for input)
    id = fields.Int(dump_only=True)
    # Vendor ID is required when creating a service
    vendor_id = fields.Int(required=True)
    # Service name: required, 1-200 characters
    service_name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    # Service description: required, minimum 10 characters
    service_description = fields.Str(required=True, validate=validate.Length(min=10))
    # Service category: required, 1-100 characters
    service_category = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    # Pricing model: must be one of the specified options
    pricing_model = fields.Str(required=True, validate=validate.OneOf(['per_hour', 'fixed', 'per_person']))
    # Base price: required, must be 0 or greater
    base_price = fields.Decimal(required=True, validate=validate.Range(min=0))
    # Availability status: optional, must be one of the specified values
    availability_status = fields.Str(validate=validate.OneOf(['Available', 'Booked', 'Unavailable']))
    # License status: read-only (only admins can set this)
    license_status = fields.Str(dump_only=True)
    # License document URL: optional, max 500 characters
    licensing_document_url = fields.Str(validate=validate.Length(max=500))
    # Contact phone: optional, max 20 characters
    contact_phone = fields.Str(validate=validate.Length(max=20))
    # Contact email: optional, must be valid email format
    contact_email = fields.Email()
    # Service location: optional, max 200 characters
    service_location = fields.Str(validate=validate.Length(max=200))
    # Timestamps: read-only, automatically set by database
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

# Single service schema instance
vendor_service_schema = VendorServiceSchema()
# Multiple services schema instance (for lists of services)
vendor_services_schema = VendorServiceSchema(many=True)