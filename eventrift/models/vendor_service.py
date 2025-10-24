from app import db
from datetime import datetime

class VendorService(db.Model):
    __tablename__ = 'vendor_services'
    
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_name = db.Column(db.String(200), nullable=False)
    service_description = db.Column(db.Text, nullable=False)
    service_category = db.Column(db.String(100), nullable=False)
    pricing_model = db.Column(db.String(50), nullable=False)  # 'per_hour', 'fixed', 'per_person'
    base_price = db.Column(db.Decimal(10, 2), nullable=False)
    availability_status = db.Column(db.String(20), default='Available')  # 'Available', 'Booked', 'Unavailable'
    license_status = db.Column(db.String(20), default='Pending')  # 'Pending', 'Verified', 'Suspended'
    licensing_document_url = db.Column(db.String(500))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    service_location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<VendorService {self.service_name}>'