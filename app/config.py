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

    # Safaricom Daraja API Configuration (M-Pesa)
# --- Base URLs ---
MPESA_BASE_URL = os.environ.get('MPESA_BASE_URL', 'https://sandbox.safaricom.co.ke')

# --- Credentials & Keys (REPLACE WITH YOUR OWN VALUES) ---
CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', 'YOUR_CONSUMER_KEY_HERE')
CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', 'YOUR_CONSUMER_SECRET_HERE')

# Short Code and Passkey for Lipa Na M-Pesa Online (STK Push)
BUSINESS_SHORT_CODE = os.environ.get('MPESA_BUSINESS_SHORT_CODE', '174379') 
LNM_PASSKEY = os.environ.get('MPESA_LNM_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919') 

# --- Endpoints & Settings ---
# IMPORTANT: This MUST be a publicly accessible URL for Safaricom to reach.
# Use ngrok or your deployed domain during development.
CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL', 'https://your-ngrok-or-domain.com/api/payments/callback') 
ACCOUNT_REFERENCE = 'EventRiftTicketPurchase' 
TRANSACTION_DESC = 'Ticket Purchase'
TRANSACTION_TYPE = 'CustomerPayBillOnline'