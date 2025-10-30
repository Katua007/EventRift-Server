import requests
import base64
from datetime import datetime, timedelta # Import timedelta
import os # Import os for environment variables in case config.py isn't used for direct access

# Import configuration variables from the app's config.py
from app.config import ( # Corrected import path
    CONSUMER_KEY, CONSUMER_SECRET, MPESA_BASE_URL, BUSINESS_SHORT_CODE, LNM_PASSKEY, 
    CALLBACK_URL, TRANSACTION_TYPE
)

class DarajaAPI:
    """
    Handles token generation, STK Push initiation, and password encoding for the M-Pesa Daraja API.
    """
    
    _access_token = None
    _token_expiry = None

    def _generate_access_token(self):
        """Generates a new access token using Consumer Key and Secret."""
        
        if DarajaAPI._access_token and DarajaAPI._token_expiry and datetime.now() < DarajaAPI._token_expiry:
            print("Using cached M-Pesa token.")
            return DarajaAPI._access_token

        key_secret = f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode('utf-8')
        encoded_auth = base64.b64encode(key_secret).decode('utf-8')
        
        token_url = f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
        
        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(token_url, headers=headers)
            response.raise_for_status() 
            data = response.json()
            
            if 'access_token' in data:
                DarajaAPI._access_token = data['access_token']
                # Token expiry is typically 3599 seconds. We use 3500 for safety.
                DarajaAPI._token_expiry = datetime.now() + timedelta(seconds=3500)
                print("M-Pesa token generated successfully.")
                return DarajaAPI._access_token
            else:
                print(f"Token generation failed: {data}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error during token generation: {e}")
            return None

    def _generate_password(self):
        """Generates the base64 encoded password required for STK Push."""
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        password_str = BUSINESS_SHORT_CODE + LNM_PASSKEY + timestamp
        encoded_password = base64.b64encode(password_str.encode('utf-8')).decode('utf-8')
        
        return encoded_password, timestamp

    def stk_push_initiate(self, amount: float, phone_number: str, account_ref: str, transaction_desc: str):
        """
        Initiates the Lipa Na M-Pesa Online (STK Push) transaction.
        """
        token = self._generate_access_token()
        if not token:
            return {"success": False, "message": "Failed to get M-Pesa access token."}
        
        password, timestamp = self._generate_password()
        
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        
        stk_push_url = f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
        
        payload = {
            "BusinessShortCode": BUSINESS_SHORT_CODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": TRANSACTION_TYPE,
            "Amount": int(amount), 
            "PartyA": phone_number,
            "PartyB": BUSINESS_SHORT_CODE,
            "PhoneNumber": phone_number,
            "CallBackURL": CALLBACK_URL,
            "AccountReference": account_ref,
            "TransactionDesc": transaction_desc
        }

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            print(f"Initiating STK Push for {phone_number} with Amount: {amount}")
            response = requests.post(stk_push_url, headers=headers, json=payload)
            response.raise_for_status()
            daraja_response = response.json()
            
            if daraja_response.get("ResponseCode") == "0":
                return {"success": True, "data": daraja_response, "message": "STK Push initiated successfully."}
            else:
                return {"success": False, "data": daraja_response, "message": daraja_response.get("errorMessage", "Daraja request failed.")}
                
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error during STK Push: {e}")
            return {"success": False, "message": f"Network error: {e}"}

mpesa_api = DarajaAPI()