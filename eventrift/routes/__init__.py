def initialize_routes(app):
    """Initialize all routes for the Flask app"""
    from eventrift.routes.vendor_routes import initialize_vendor_routes
    initialize_vendor_routes(app.api)