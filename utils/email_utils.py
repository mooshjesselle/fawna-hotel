import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, session
from datetime import datetime, timedelta
import requests

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_otp_email(email, otp):
    sender_email = current_app.config['MAIL_USERNAME']
    sender_password = current_app.config['MAIL_PASSWORD']

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = "FAWNA Hotel - Email Verification OTP"

    body = f"""
    <html>
        <body>
            <h2>Welcome to FAWNA Hotel!</h2>
            <p>Your email verification OTP is: <strong>{otp}</strong></p>
            <p>This OTP will expire in 10 minutes.</p>
            <p>If you didn't request this OTP, please ignore this email.</p>
        </body>
    </html>
    """
    
    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_email_via_sendgrid(to_email, subject, html_body):
    api_key = current_app.config.get('SENDGRID_API_KEY', '')
    from_email = current_app.config.get('SENDGRID_FROM_EMAIL', current_app.config.get('MAIL_DEFAULT_SENDER'))
    if not api_key or not from_email:
        return False
    try:
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": from_email},
            "subject": subject,
            "content": [{"type": "text/html", "value": html_body}]
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        resp = requests.post("https://api.sendgrid.com/v3/mail/send", json=payload, headers=headers, timeout=10)
        return 200 <= resp.status_code < 300
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False

def store_otp(email, otp):
    # Store OTP in session with 10-minute expiration
    session['otp_data'] = {
        'email': email,
        'otp': otp,
        'expires_at': (datetime.now() + timedelta(minutes=10)).timestamp()
    }

def verify_otp(email, otp):
    otp_data = session.get('otp_data')
    if not otp_data:
        return False
        
    if (otp_data['email'] != email or 
        otp_data['otp'] != otp or 
        datetime.now().timestamp() > otp_data['expires_at']):
        return False
        
    # Clear OTP data after successful verification
    session.pop('otp_data', None)
    return True 