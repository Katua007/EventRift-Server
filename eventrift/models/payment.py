from datetime import datetime
from eventrift.extensions import db

class Payment(db.Model):
    """Tracks M-Pesa payment transactions for ticket purchases."""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    
    # Unique reference generated during initiation (Crucial for callback matching)
    checkout_request_id = db.Column(db.String(50), unique=True, nullable=True)
    merchant_request_id = db.Column(db.String(50), nullable=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    # Core payment details
    amount = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)  # Number of tickets
    phone_number = db.Column(db.String(15), nullable=False)
    status = db.Column(db.String(20), default='PENDING', nullable=False)  # PENDING, PAID, FAILED, CANCELLED
    
    # Confirmation details
    mpesa_receipt_number = db.Column(db.String(20), unique=True, nullable=True)
    transaction_date = db.Column(db.DateTime, nullable=True)  # Transaction completion time
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('payments', lazy=True))
    event = db.relationship('Event', backref=db.backref('payments', lazy=True))
    tickets = db.relationship('Ticket', backref='payment', lazy=True)

    def __repr__(self):
        return f"<Payment {self.id} - Status: {self.status} - Amount: {self.amount}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()