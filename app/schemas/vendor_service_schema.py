from marshmallow import Schema, fields, validate

class VendorServiceSchema(Schema):
    id = fields.Int(dump_only=True)
    vendor_id = fields.Int(required=True)
    service_name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    service_description = fields.Str(required=True, validate=validate.Length(min=10))
    service_category = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    pricing_model = fields.Str(required=True, validate=validate.OneOf(['per_hour', 'fixed', 'per_person']))
    base_price = fields.Decimal(required=True, validate=validate.Range(min=0))
    availability_status = fields.Str(validate=validate.OneOf(['Available', 'Booked', 'Unavailable']))
    license_status = fields.Str(dump_only=True)
    licensing_document_url = fields.Str(validate=validate.Length(max=500))
    contact_phone = fields.Str(validate=validate.Length(max=20))
    contact_email = fields.Email()
    service_location = fields.Str(validate=validate.Length(max=200))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

vendor_service_schema = VendorServiceSchema()
vendor_services_schema = VendorServiceSchema(many=True)