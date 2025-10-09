import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, session
import os
import requests
from datetime import datetime, timedelta

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

def send_html_email(subject, recipient, html_body):
    """Send an HTML email.

    In production on Render, outbound SMTP is blocked on common ports. This helper
    first tries an HTTP email provider (Resend) when RESEND_API_KEY is present.
    If not configured, it falls back to Flask-Mail-compatible SMTP for local dev.
    """
    api_key = os.getenv('RESEND_API_KEY') or current_app.config.get('RESEND_API_KEY')
    sender = (current_app.config.get('EMAIL_FROM') or
              current_app.config.get('MAIL_DEFAULT_SENDER') or
              current_app.config.get('MAIL_USERNAME'))

    if api_key:
        try:
            response = requests.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'from': sender,
                    'to': [recipient],
                    'subject': subject,
                    'html': html_body
                },
                timeout=20
            )
            if 200 <= response.status_code < 300:
                return True
            print(f"Resend API error {response.status_code}: {response.text}")
            return False
        except Exception as e:
            print(f"Resend API exception: {e}")
            # fall through to SMTP fallback

    # Fallback to SMTP (local development)
    try:
        sender_email = current_app.config['MAIL_USERNAME']
        sender_password = current_app.config['MAIL_PASSWORD']
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"SMTP fallback error: {e}")
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