from flask import Flask
from flask_restful import Api
# ... other imports for db, migrate, jwt ...

# Import all necessary route blueprints
from app.routes.payments_routes import payments_bp 
from app.routes.ticket_routes import ticket_bp
# Assuming you have a user blueprint:
# from app.routes.user_routes import user_bp 

# Initialize Flask extensions outside create_app if they need to be globally accessible
# (e.g., db, migrate, jwt)

def create_app():
    app = Flask(__name__)
    # ... your existing app configurations from app.config ...

    # Initialize extensions with the app
    # db.init_app(app)
    # migrate.init_app(app, db)
    # jwt.init_app(app)
    
    # Register blueprints/routes
    
    # Example for API resources (if you're using Flask-RESTful with blueprints directly)
    # app.register_blueprint(user_bp, url_prefix='/api/users') 
    
    # Register the payments blueprint (M-Pesa Daraja API)
    app.register_blueprint(payments_bp, url_prefix='/api/payments') 

    # Register the new ticket blueprint (Ticket/Attendance Logic)
    app.register_blueprint(ticket_bp, url_prefix='/api/tickets')

    return app
