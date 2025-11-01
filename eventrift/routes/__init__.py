def initialize_routes(app):
    """Initialize all routes for the Flask app"""
    from eventrift.routes.auth_routes import auth_bp
    from eventrift.routes.vendor_routes import initialize_vendor_routes

    # Register auth blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Initialize vendor routes
    initialize_vendor_routes(app.api)
    
    # Register other route blueprints if they exist
    try:
        from eventrift.routes.event_routes import events_bp
        app.register_blueprint(events_bp, url_prefix='/api')
    except ImportError:
        pass
    
    try:
        from eventrift.routes.category_routes import categories_bp
        app.register_blueprint(categories_bp, url_prefix='/api')
    except ImportError:
        pass
    
    try:
        from eventrift.routes.ticket_routes import tickets_bp
        app.register_blueprint(tickets_bp, url_prefix='/api')
    except ImportError:
        pass
    
    try:
        from eventrift.routes.stall_routes import stalls_bp
        app.register_blueprint(stalls_bp, url_prefix='/api')
    except ImportError:
        pass
    
    try:
        from eventrift.routes.payments_routes import payments_bp
        app.register_blueprint(payments_bp, url_prefix='/api')
    except ImportError:
        pass
    
    try:
        from eventrift.routes.user_routes import users_bp
        app.register_blueprint(users_bp, url_prefix='/api')
    except ImportError:
        pass