import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'postgresql://user:pass@localhost:5432/eventrift_dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-super-secret-key-change-me')
    
    # Other Configs
    SECRET_KEY = os.environ.get('SECRET_KEY', 'another-default-secret')

# =========================================================================
# --- Safaricom Daraja API Global Configuration ---
# These constants are used by utility files (daraja_api.py, routes) via direct import.
# =========================================================================

# --- Base Credentials & Keys (Shared) ---
MPESA_BASE_URL = os.environ.get('MPESA_BASE_URL', 'https://sandbox.safaricom.co.ke')
CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', 'YOUR_CONSUMER_KEY_HERE')
CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', 'YOUR_CONSUMER_SECRET_HERE')
BUSINESS_SHORT_CODE = os.environ.get('MPESA_BUSINESS_SHORT_CODE', '174379') 
LNM_PASSKEY = os.environ.get('MPESA_LNM_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919') 
TRANSACTION_TYPE = 'CustomerPayBillOnline' # Used for STK Push

# --- TICKET Payment Settings (Used primarily by payments_routes.py) ---
# Callback URL for M-Pesa to reach the /api/payments/callback endpoint
TICKET_CALLBACK_URL = os.environ.get('MPESA_TICKET_CALLBACK_URL', 'https://your-domain.com/api/payments/callback') 
TICKET_ACCOUNT_REFERENCE = 'EventRiftTicketPurchase' 
TICKET_TRANSACTION_DESC = 'Ticket Purchase'

# --- STALL Payment Settings (Used by stall_routes.py) ---
# Callback URL for M-Pesa to reach the /api/stalls/callback endpoint
STALL_CALLBACK_URL = os.environ.get('MPESA_STALL_CALLBACK_URL', 'https://your-domain.com/api/stalls/callback')
STALL_ACCOUNT_REFERENCE = 'EventRiftStallBooking'
STALL_TRANSACTION_DESC = 'Stall Booking Payment'

# --- Backwards Compatibility Aliases ---
# The original Daraja utility files expected these generic names. We alias them to the TICKET settings.
CALLBACK_URL = TICKET_CALLBACK_URL
ACCOUNT_REFERENCE = TICKET_ACCOUNT_REFERENCE
TRANSACTION_DESC = TICKET_TRANSACTION_DESC

# --- Cloudinary Configuration (BE-301) ---
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
