# Import database instance from extensions
from eventrift.extensions import db
# Import datetime for timestamps
from datetime import datetime

# VendorService model represents services offered by vendors (catering, photography, etc.)
class VendorService(db.Model):
    # Database table name
    __tablename__ = 'vendor_services'

    # Primary key - unique identifier for each service
    id = db.Column(db.Integer, primary_key=True)
    # Foreign key linking to the vendor (user) who offers this service
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Service name (required, max 200 characters)
    service_name = db.Column(db.String(200), nullable=False)
    # Detailed description of the service (required)
    service_description = db.Column(db.Text, nullable=False)
    # Category/type of service (catering, photography, etc.)
    service_category = db.Column(db.String(100), nullable=False)
    # How the service is priced: per_hour, fixed price, or per_person
    pricing_model = db.Column(db.String(50), nullable=False)
    # Base price for the service
    base_price = db.Column(db.Float, nullable=False)
    # Current availability status of the service
    availability_status = db.Column(db.String(20), default='Available')
    # License verification status (set by admins)
    license_status = db.Column(db.String(20), default='Pending')
    # URL to uploaded license document
    licensing_document_url = db.Column(db.String(500))
    # Contact phone number for the service
    contact_phone = db.Column(db.String(20))
    # Contact email for the service
    contact_email = db.Column(db.String(120))
    # Location where service is offered
    service_location = db.Column(db.String(200))
    # Timestamp when service was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Timestamp when service was last updated
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # String representation for debugging
    def __repr__(self):
        return f'<VendorService {self.service_name}>'
