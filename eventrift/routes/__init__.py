def initialize_routes(app):
    """Initialize all routes for the Flask app"""
    from eventrift.routes.auth_routes import auth_bp
    from eventrift.routes.vendor_routes import initialize_vendor_routes

    # Register auth blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Initialize vendor routes
    initialize_vendor_routes(app.api)