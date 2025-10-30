import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv() # Ensure environment variables are loaded if running outside Flask context

# Assumes SENDGRID_API_KEY and SENDER_EMAIL are in .env
def send_verification_email(user_email, verification_token):
    """Sends an email with a unique verification link."""
    try:
        # NOTE: The verification link must point to a backend route you will create later (e.g., /verify/<token>)
        # For now, use the placeholder URL:
        verification_link = f"https://your.eventrift.com/api/verify/{verification_token}" 
        
        message = Mail(
            from_email=os.getenv('SENDER_EMAIL', 'no-reply@eventrift.com'),
            to_emails=user_email,
            subject='EventRift: Please Verify Your Email Address',
            html_content=(
                f'<strong>Welcome to EventRift!</strong><br>'
                f'Thank you for signing up. Please verify your email address by clicking the link below:<br><br>'
                f'<a href="{verification_link}">VERIFY MY EMAIL</a><br><br>'
                f'If you did not sign up for EventRift, please ignore this email.'
            )
        )
        
        # Initialize SendGrid client
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        
        # Log successful sending attempt
        print(f"Verification email sent to {user_email}. Status Code: {response.status_code}")
        return True # Return success status
        
    except Exception as e:
        # Log and handle any SendGrid errors
        print(f"SendGrid Error sending email to {user_email}: {e}")
        return False # Return failure status