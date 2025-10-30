from marshmallow import Schema, fields

class PaginationSchema(Schema):
    """Schema for pagination metadata."""
    total_items = fields.Int(attribute='total', dump_only=True)
    total_pages = fields.Int(attribute='pages', dump_only=True)
    current_page = fields.Int(attribute='page', dump_only=True)
    has_next = fields.Bool(dump_only=True)
    has_prev = fields.Bool(dump_only=True)

pagination_schema = PaginationSchema()