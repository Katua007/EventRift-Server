from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db # Database session
from app.models.stall_booking import StallBooking, StallPayment, StallType
from app.schemas.stall_schemas import stall_booking_schema, stall_bookings_schema, stall_types_schema
# Import shared Daraja Utility and Config constants
from app.utils.daraja_api import mpesa_api
from app.config import ACCOUNT_REFERENCE 

from sqlalchemy.orm import joinedload
from datetime import datetime
import json

# Create the Blueprint for stall-related routes
stall_bp = Blueprint('stall_bp', __name__)
api = Api(stall_bp)

class StallBookingListResource(Resource):
    @jwt_required()
    def post(self):
        """1. Creates a pending StallBooking and StallPayment record and initiates STK Push."""
        vendor_id = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['event_id', 'stall_type_id', 'business_name', 'products_offered', 'mpesa_phone']
        if not all(field in data for field in required_fields):
            return {"message": "Missing required booking details (event_id, type_id, business_name, products, phone)."}, 400

        # Validate stall type and get price
        stall_type = StallType.query.get(data['stall_type_id'])
        if not stall_type:
            return {"message": "Invalid stall type selected."}, 404
        
        total_amount = stall_type.price 
        phone_number = data['mpesa_phone']
        
        # --- Create Pending Records ---
        try:
            # 1. Create PENDING StallPayment record
            new_payment = StallPayment(
                amount=total_amount,
                phone_number=phone_number,
                status='PENDING'
            )
            db.session.add(new_payment)
            db.session.flush() # Flushes to get new_payment.id
            
            # 2. Create PENDING_PAYMENT StallBooking record
            new_booking = StallBooking(
                vendor_id=vendor_id,
                event_id=data['event_id'],
                stall_type_id=data['stall_type_id'],
                payment_id=new_payment.id,
                business_name=data['business_name'],
                products_offered=data['products_offered'],
                status='PENDING_PAYMENT'
            )
            db.session.add(new_booking)
            db.session.commit()
            
            # --- Initiate M-Pesa STK Push ---
            unique_ref = f"STALL-{new_booking.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            test_amount = 1 # Use total_amount in production after testing
            
            daraja_result = mpesa_api.stk_push_initiate(
                amount=test_amount, 
                phone_number=phone_number,
                account_ref=unique_ref,
                transaction_desc=f"Stall Booking: {stall_type.name} for Event {data['event_id']}"
            )

            if daraja_result['success']:
                # Update PENDING payment record with Daraja IDs
                new_payment.checkout_request_id = daraja_result['data'].get('CheckoutRequestID')
                new_payment.merchant_request_id = daraja_result['data'].get('MerchantRequestID')
                new_payment.status = 'AWAITING_CONFIRMATION'
                db.session.commit()
                
                return {
                    "success": True, 
                    "message": "M-Pesa prompt sent. Complete payment on your phone.",
                    "CheckoutRequestID": new_payment.checkout_request_id,
                    "booking_id": new_booking.id
                }, 202 
            else:
                # If STK Push fails immediately, mark payment/booking as failed and rollback
                db.session.rollback() 
                return {
                    "success": False, 
                    "message": f"Payment initiation failed: {daraja_result['message']}",
                    "daraja_response": daraja_result['data']
                }, 500
                
        except Exception as e:
            db.session.rollback()
            print(f"Error processing stall booking: {e}")
            return {"success": False, "message": "Internal server error during booking setup."}, 500

    @jwt_required()
    def get(self):
        """Retrieves all stall bookings for the authenticated vendor."""
        vendor_id = get_jwt_identity()
        # Fetch bookings and eagerly load related payment and stall type data
        bookings = StallBooking.query.filter_by(vendor_id=vendor_id).options(
            joinedload(StallBooking.payment),
            joinedload(StallBooking.stall_type)
        ).all()
        return jsonify(stall_bookings_schema.dump(bookings)), 200

class StallBookingCallbackResource(Resource):
    def post(self):
        """2. Receives the M-Pesa payment confirmation and finalizes the booking."""
        try:
            callback_data = request.get_json()
            
            # Extract STK callback data safely
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            
            # 1. Find the PENDING payment record using the unique CheckoutRequestID
            payment_record = StallPayment.query.filter_by(checkout_request_id=checkout_request_id).first()
            if not payment_record:
                print(f"ERROR: Callback received for unknown Stall CheckoutRequestID: {checkout_request_id}")
                return {"ResultCode": 1, "ResultDesc": "Invalid reference"}, 200
            
            booking_record = payment_record.booking
            
            if result_code == 0:
                # SUCCESSFUL PAYMENT
                callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                
                def find_item(name):
                    return next((item['Value'] for item in callback_metadata if item.get('Name') == name), None)
                
                mpesa_receipt_number = find_item('MpesaReceiptNumber')
                transaction_date_str = find_item('TransactionDate')
                
                # --- Finalize Booking ---
                try:
                    # Update Payment Status
                    payment_record.status = 'PAID'
                    payment_record.mpesa_receipt_number = mpesa_receipt_number
                    
                    # Convert Daraja timestamp (YYYYMMDDHHMMSS) to datetime object
                    if transaction_date_str:
                        payment_record.transaction_date = datetime.strptime(transaction_date_str, '%Y%m%d%H%M%S')
                    
                    # Update Booking Status
                    booking_record.status = 'CONFIRMED'
                    
                    db.session.commit()
                    print(f"Stall Booking {booking_record.id} CONFIRMED. Receipt: {mpesa_receipt_number}")
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"FATAL DB ERROR: Failed to finalize booking {booking_record.id} after success: {e}")

            else:
                # FAILED or CANCELLED TRANSACTION
                payment_record.status = 'FAILED'
                booking_record.status = 'CANCELLED' 
                db.session.commit()
                print(f"Transaction FAILED for booking {booking_record.id}. Code: {result_code}")
                
            # Safaricom expects a simple 200 OK response
            return {"ResultCode": 0, "ResultDesc": "Callback received and processed."}, 200

        except Exception as e:
            print(f"Error processing Stall M-Pesa callback: {e}")
            return {"ResultCode": 1, "ResultDesc": "Internal Server Error during processing"}, 200

# Route for fetching available stall types for an event
class StallTypeResource(Resource):
    def get(self, event_id):
        """Fetches all available stall types for a specific event."""
        # NOTE: In a real app, you would filter stall types by event_id, but here we return all types for now
        stall_types = StallType.query.all() 
        return jsonify(stall_types_schema.dump(stall_types)), 200

# Register the resources with the API blueprint
# POST /api/stalls/ - Initiate booking
# GET /api/stalls/ - Get vendor bookings
api.add_resource(StallBookingListResource, '/') 

# POST /api/stalls/callback - M-Pesa callback URL
api.add_resource(StallBookingCallbackResource, '/callback') 

# GET /api/stalls/types/<event_id> - Get available stall options
api.add_resource(StallTypeResource, '/types/<int:event_id>')
