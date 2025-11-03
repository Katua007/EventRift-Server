def initialize_routes(app):
    """Initialize all routes for the Flask app"""
    from eventrift.routes.auth_routes import auth_bp
    from eventrift.routes.vendor_routes import initialize_vendor_routes

    # Register auth blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Initialize vendor routes - get the api object from extensions
    try:
        from eventrift.extensions import api
        initialize_vendor_routes(api)
    except ImportError:
        # Fallback: skip vendor routes if extensions not available
        pass
    
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
        from eventrift.routes.ticket_routes import ticket_bp
        app.register_blueprint(ticket_bp, url_prefix='/api/tickets')
    except ImportError:
        pass
    
    try:
        from eventrift.routes.stall_routes import stalls_bp
        app.register_blueprint(stalls_bp, url_prefix='/api')
    except ImportError:
        pass
    
    try:
        from eventrift.routes.payments_routes import payments_bp
        app.register_blueprint(payments_bp, url_prefix='/api/payments')
    except ImportError:
        pass
    
    try:
        from eventrift.routes.user_routes import users_bp
        app.register_blueprint(users_bp, url_prefix='/api')
    except ImportError:
        pass
    
    try:
        from eventrift.routes.data_retrieval_routes import data_retrieval_bp
        app.register_blueprint(data_retrieval_bp, url_prefix='/api/data')
    except ImportError:
        pass
    
    try:
        from eventrift.routes.dashboard_routes import dashboard_bp
        app.register_blueprint(dashboard_bp, url_prefix='/api')
    except ImportError:
        pass
    
    try:
        from eventrift.routes.test_routes import test_bp
        app.register_blueprint(test_bp, url_prefix='/api/test')
    except ImportError:
        pass