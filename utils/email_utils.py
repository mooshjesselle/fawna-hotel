import smtplib
import random
import socket
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, session
from datetime import datetime, timedelta
from functools import wraps
import time

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def timeout_handler(func):
    """Decorator to handle email sending timeouts"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = [False]
        exception = [None]
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=30)  # 30 second timeout
        
        if thread.is_alive():
            print("Email sending timed out")
            return False
        
        if exception[0]:
            print(f"Email sending error: {exception[0]}")
            return False
            
        return result[0]
    return wrapper

@timeout_handler
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
        # Use TLS instead of SSL for better compatibility
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'], timeout=30) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        return True
    except (smtplib.SMTPException, socket.error, OSError) as e:
        print(f"Error sending email: {e}")
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

@timeout_handler
def send_email_with_flask_mail(mail, msg):
    """Send email using Flask-Mail with timeout handling"""
    try:
        mail.send(msg)
        return True
    except (smtplib.SMTPException, socket.error, OSError) as e:
        print(f"Flask-Mail error: {e}")
        return False

def send_email_async(mail, msg):
    """Send email asynchronously to prevent timeouts"""
    def send_in_background():
        from flask import current_app
        with current_app.app_context():
            try:
                # Add timeout to the mail connection
                import socket
                original_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(30)  # 30 second timeout
                
                try:
                    mail.send(msg)
                    print("Email sent successfully")
                finally:
                    socket.setdefaulttimeout(original_timeout)
            except Exception as e:
                print(f"Background email sending failed: {e}")
                # Try alternative email sending method
                try_alternative_email_sending(msg)
    
    thread = threading.Thread(target=send_in_background)
    thread.daemon = True
    thread.start()
    return True

def send_email_async_with_context(mail, msg, app):
    """Send email asynchronously with proper application context"""
    def send_in_background():
        with app.app_context():
            try:
                # Add timeout to the mail connection
                import socket
                original_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(30)  # 30 second timeout
                
                try:
                    mail.send(msg)
                    print("Email sent successfully")
                finally:
                    socket.setdefaulttimeout(original_timeout)
            except Exception as e:
                print(f"Background email sending failed: {e}")
                # Try alternative email sending method
                try_alternative_email_sending_with_context(msg, app)
    
    thread = threading.Thread(target=send_in_background)
    thread.daemon = True
    thread.start()
    return True

def try_alternative_email_sending(msg):
    """Try alternative email sending methods"""
    try:
        # Try using direct SMTP connection as fallback
        from flask import current_app
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        with current_app.app_context():
            # Create a simple text version of the email
            simple_msg = MIMEMultipart()
            simple_msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
            simple_msg['To'] = ', '.join(msg.recipients)
            simple_msg['Subject'] = msg.subject
            
            # Convert HTML to text if possible
            if hasattr(msg, 'html') and msg.html:
                import re
                # Simple HTML to text conversion
                text_content = re.sub(r'<[^>]+>', '', str(msg.html))
                simple_msg.attach(MIMEText(text_content, 'plain'))
            else:
                simple_msg.attach(MIMEText('Email content', 'plain'))
            
            # Try to send using direct SMTP
            with smtplib.SMTP(current_app.config['MAIL_SERVER'], 
                              current_app.config['MAIL_PORT'], 
                              timeout=30) as server:
                if current_app.config.get('MAIL_USE_TLS'):
                    server.starttls()
                server.login(current_app.config['MAIL_USERNAME'], 
                            current_app.config['MAIL_PASSWORD'])
                server.send_message(simple_msg)
                print("Alternative email sending successful")
            
    except Exception as e:
        print(f"Alternative email sending also failed: {e}")

def try_alternative_email_sending_with_context(msg, app):
    """Try alternative email sending methods with proper application context"""
    try:
        # Try using direct SMTP connection as fallback
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        with app.app_context():
            # Create a simple text version of the email
            simple_msg = MIMEMultipart()
            simple_msg['From'] = app.config['MAIL_DEFAULT_SENDER']
            simple_msg['To'] = ', '.join(msg.recipients)
            simple_msg['Subject'] = msg.subject
            
            # Convert HTML to text if possible
            if hasattr(msg, 'html') and msg.html:
                import re
                # Simple HTML to text conversion
                text_content = re.sub(r'<[^>]+>', '', str(msg.html))
                simple_msg.attach(MIMEText(text_content, 'plain'))
            else:
                simple_msg.attach(MIMEText('Email content', 'plain'))
            
            # Try to send using direct SMTP
            with smtplib.SMTP(app.config['MAIL_SERVER'], 
                              app.config['MAIL_PORT'], 
                              timeout=30) as server:
                if app.config.get('MAIL_USE_TLS'):
                    server.starttls()
                server.login(app.config['MAIL_USERNAME'], 
                            app.config['MAIL_PASSWORD'])
                server.send_message(simple_msg)
                print("Alternative email sending successful")
            
    except Exception as e:
        print(f"Alternative email sending also failed: {e}") 