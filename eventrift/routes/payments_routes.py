from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
import datetime
import json
from app import db # ADDED: Necessary for database session operations
from app.models.ticket_attendance import Ticket, Attendance # Import models for ticket creation

# Import the Daraja utility and config
from app.utils.daraja_api import mpesa_api
from app.config import ACCOUNT_REFERENCE, TRANSACTION_DESC

# Create a Blueprint for payment routes
payments_bp = Blueprint('payments_bp', __name__)
api = Api(payments_bp)

class InitiatePaymentResource(Resource):
    def post(self):
        """Receives payment request from the frontend and calls the Daraja STK Push API."""
        try:
            data = request.get_json()
            
            required_fields = ['event_id', 'user_id', 'quantity', 'mpesa_phone', 'total_amount']
            if not all(field in data for field in required_fields):
                return {"success": False, "message": "Missing required fields."}, 400

            total_amount = data['total_amount']
            phone_number = data['mpesa_phone']
            event_id = data['event_id']
            user_id = data['user_id']
            
            # --- IMPORTANT: Before calling Daraja, save a pending transaction record to your DB ---
            # This unique_ref should link to your DB transaction record.
            # Example: A simple unique reference for now, but should be a proper DB ID
            unique_ref = f"{ACCOUNT_REFERENCE}-{event_id}-{user_id}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

            # For Sandbox testing, always use a minimum amount of 1 KES
            test_amount = 1 # Use total_amount in production after successful testing
            
            daraja_result = mpesa_api.stk_push_initiate(
                amount=test_amount, # Use total_amount in production
                phone_number=phone_number,
                account_ref=unique_ref,
                transaction_desc=TRANSACTION_DESC
            )

            if daraja_result['success']:
                # --- IMPORTANT: Update your pending DB transaction with CheckoutRequestID ---
                # This ID is crucial for matching the callback
                checkout_request_id = daraja_result['data'].get('CheckoutRequestID')
                # Save checkout_request_id and unique_ref to your DB for this pending payment
                
                print(f"STK Push Sent. CheckoutRequestID: {checkout_request_id}")
                
                return {
                    "success": True, 
                    "message": daraja_result['message'],
                    "CheckoutRequestID": checkout_request_id
                }, 200
            else:
                return {
                    "success": False, 
                    "message": f"Payment initiation failed: {daraja_result['message']}",
                    "daraja_response": daraja_result['data'] # Include Daraja's raw error for debugging
                }, 500

        except Exception as e:
            print(f"Error initiating payment: {e}")
            return {"success": False, "message": "Internal server error."}, 500

class MpesaCallbackResource(Resource):
    def post(self):
        """Receives the final payment result from Safaricom and updates the database."""
        try:
            callback_data = request.get_json()
            
            print("-" * 50)
            print("Received M-Pesa Callback:")
            
            # Extract STK callback data safely
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            
            print(json.dumps(callback_data, indent=4))
            print("-" * 50)
            
            # Extract results (handle potential missing keys carefully)
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            
            if result_code == 0:
                # SUCCESSFUL TRANSACTION
                print(f"Transaction SUCCESS for CheckoutRequestID: {checkout_request_id}")
                
                callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                
                def find_item(name):
                    return next((item['Value'] for item in callback_metadata if item.get('Name') == name), None)
                
                mpesa_receipt_number = find_item('MpesaReceiptNumber')
                amount = find_item('Amount')
                transaction_date = find_item('TransactionDate')
                phone_number = find_item('PhoneNumber')
                
                # 1. Find the pending transaction record in your DB using `checkout_request_id`.
                #    (Requires a Payment model, let's assume it has an associated `quantity` and `user_id`)
                #    payment_record = Payment.query.filter_by(checkout_request_id=checkout_request_id).first()
                
                # --- TICKET CREATION LOGIC (BE-402) ---
                
                # Placeholder variables that would come from the Payment record:
                # user_id = payment_record.user_id
                # event_id = payment_record.event_id
                # quantity = payment_record.quantity
                # payment_id = payment_record.id 

                # Simulating data retrieval for demonstration:
                user_id = 1 
                event_id = 101
                quantity = 2
                payment_id = 50 

                if True: # Replace with check: if payment_record and payment_record.status != 'PAID':
                    try:
                        # Update payment record status and details
                        # payment_record.status = 'PAID'
                        # payment_record.mpesa_receipt = mpesa_receipt_number
                        # payment_record.transaction_date = transaction_date
                        
                        # Create the specified number of Ticket records
                        new_tickets = []
                        for _ in range(quantity):
                            new_ticket = Ticket(
                                user_id=user_id,
                                event_id=event_id,
                                payment_id=payment_id,
                                status='PAID',
                                ticket_type='General Admission' # Adjust based on payment_record if necessary
                            )
                            db.session.add(new_ticket)
                            new_tickets.append(new_ticket)
                        
                        db.session.flush() # Generate IDs for tickets (needed for Attendance foreign key)
                        
                        # Create corresponding Attendance records
                        for ticket in new_tickets:
                            new_attendance = Attendance(ticket_id=ticket.id, is_checked_in=False)
                            db.session.add(new_attendance)

                        db.session.commit()
                        print(f"Successfully created {quantity} tickets for user {user_id} and event {event_id}.")
                    except Exception as e:
                        db.session.rollback()
                        print(f"FATAL ERROR: Failed to create tickets after successful payment: {e}")
                        # You MUST log this and have an offline process to reconcile tickets!

                # --- END TICKET CREATION LOGIC ---
                
            else:
                # FAILED TRANSACTION 
                print(f"Transaction FAILED for CheckoutRequestID: {checkout_request_id}. Reason: {result_desc}")
                
                # 1. Find the pending transaction record in your DB using `checkout_request_id`.
                # 2. Update its status to 'FAILED' and log the reason (`result_desc`).
                
            # Safaricom expects a simple 200 OK response from the callback URL
            return {"ResultCode": 0, "ResultDesc": "Callback received successfully."}, 200

        except Exception as e:
            print(f"Error processing M-Pesa callback: {e}")
            # Always return 200 OK to M-Pesa to prevent retries, even on internal failure
            return {"ResultCode": 1, "ResultDesc": "Internal Server Error"}, 200

# Register the resources with the API blueprint
api.add_resource(InitiatePaymentResource, '/initiate')
api.add_resource(MpesaCallbackResource, '/callback')
