# Import Marshmallow for data validation and serialization
from marshmallow import Schema, fields, validate

# Schema for validating and serializing EventCategory data
class CategorySchema(Schema):
    # ID is read-only (only shown when returning data, not required for input)
    id = fields.Int(dump_only=True)
    # Category name: required, 1-100 characters
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    # Category description: optional, max 500 characters
    description = fields.Str(validate=validate.Length(max=500))
    # Timestamps: read-only, automatically set by database
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

# Single category schema instance
category_schema = CategorySchema()
# Multiple categories schema instance (for lists of categories)
categories_schema = CategorySchema(many=True)