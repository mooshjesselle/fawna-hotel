import os
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, session
from datetime import datetime, timedelta
import requests
from utils.extensions import mail
from flask_mail import Message

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_otp_email(email, otp):
    subject = "FAWNA Hotel - Email Verification OTP"
    html = f"""
    <html>
        <body>
            <h2>Welcome to FAWNA Hotel!</h2>
            <p>Your email verification OTP is: <strong>{otp}</strong></p>
            <p>This OTP will expire in 10 minutes.</p>
            <p>If you didn't request this OTP, please ignore this email.</p>
        </body>
    </html>
    """
    return send_html_email(email, subject, html)

def send_html_email(recipient, subject, html_body):
    """Send HTML email using provider API if available, otherwise Flask-Mail, otherwise direct SMTP.
    Returns True on success, False on failure.
    """
    try:
        # 1) Try SendGrid API if configured
        sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        if sendgrid_api_key:
            sg_payload = {
                "personalizations": [{"to": [{"email": recipient}]}],
                "from": {"email": current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')},
                "subject": subject,
                "content": [{"type": "text/html", "value": html_body}]
            }
            resp = requests.post(
                'https://api.sendgrid.com/v3/mail/send',
                headers={
                    'Authorization': f'Bearer {sendgrid_api_key}',
                    'Content-Type': 'application/json'
                },
                json=sg_payload,
                timeout=10
            )
            if 200 <= resp.status_code < 300:
                return True
            print(f"SendGrid send failed: {resp.status_code} {resp.text}")

        # 2) Try Mailgun API if configured
        mailgun_api_key = os.getenv('MAILGUN_API_KEY')
        mailgun_domain = os.getenv('MAILGUN_DOMAIN')
        if mailgun_api_key and mailgun_domain:
            mg_from = current_app.config.get('MAIL_DEFAULT_SENDER') or f"no-reply@{mailgun_domain}"
            resp = requests.post(
                f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
                auth=("api", mailgun_api_key),
                data={
                    "from": mg_from,
                    "to": [recipient],
                    "subject": subject,
                    "html": html_body
                },
                timeout=10
            )
            if 200 <= resp.status_code < 300:
                return True
            print(f"Mailgun send failed: {resp.status_code} {resp.text}")

        # 3) Fallback to Flask-Mail (SMTP)
        try:
            msg = Message(subject, recipients=[recipient])
            msg.html = html_body
            mail.send(msg)
            return True
        except Exception as smtp_err:
            print(f"Flask-Mail SMTP send failed: {smtp_err}")

        # 4) Final fallback: direct SMTP using configured creds (SSL or TLS)
        sender_email = current_app.config.get('MAIL_USERNAME')
        sender_password = current_app.config.get('MAIL_PASSWORD')
        if not sender_email or not sender_password:
            return False

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(html_body, "html"))

        try:
            # Prefer TLS (587) to avoid SSL restrictions
            with smtplib.SMTP(current_app.config.get('MAIL_SERVER', 'smtp.gmail.com'), current_app.config.get('MAIL_PORT', 587)) as server:
                server.ehlo()
                if current_app.config.get('MAIL_USE_TLS', True):
                    server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            return True
        except Exception as direct_err:
            print(f"Direct SMTP send failed: {direct_err}")
            return False
    except Exception as e:
        print(f"send_html_email unexpected error: {e}")
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