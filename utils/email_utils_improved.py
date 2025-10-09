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

def send_email_async_with_context(mail, msg, app):
    """Send email asynchronously with proper application context and immediate fallback"""
    def send_in_background():
        print("🔄 Background email thread started")
        try:
            with app.app_context():
                success = False
                try:
                    # Try Flask-Mail first with shorter timeout
                    import socket
                    original_timeout = socket.getdefaulttimeout()
                    socket.setdefaulttimeout(10)  # Reduced to 10 seconds
                    
                    try:
                        mail.send(msg)
                        print("✅ Email sent successfully via Flask-Mail")
                        success = True
                    except Exception as e:
                        print(f"Flask-Mail failed: {e}")
                    finally:
                        socket.setdefaulttimeout(original_timeout)
                    
                    # If Flask-Mail failed, try SendGrid API first (since SMTP is blocked on Render)
                    if not success:
                        print("Trying SendGrid API (SMTP is blocked on Render)...")
                        from utils.simple_email_service import send_email_via_sendgrid_api
                        success = send_email_via_sendgrid_api(
                            ', '.join(msg.recipients), 
                            msg.subject, 
                            str(msg.html) if hasattr(msg, 'html') and msg.html else 'Email content',
                            app
                        )
                        if success:
                            print("✅ Email sent successfully via SendGrid API")
                        else:
                            print("❌ SendGrid API failed, trying SMTP fallback...")
                            success = try_direct_smtp_sending(msg, app)
                            if success:
                                print("✅ Email sent successfully via SMTP fallback")
                            else:
                                print("❌ All methods failed, using simple fallback...")
                                from utils.simple_email_service import send_email_simple_fallback
                                success = send_email_simple_fallback(
                                    ', '.join(msg.recipients), 
                                    msg.subject, 
                                    str(msg.html) if hasattr(msg, 'html') and msg.html else 'Email content',
                                    app
                                )
                            
                except Exception as e:
                    print(f"Background email sending failed: {e}")
                    # Final fallback
                    if not success:
                        success = try_direct_smtp_sending(msg, app)
                        if success:
                            print("✅ Email sent successfully via final fallback")
                        else:
                            print("❌ All SMTP methods failed, trying SendGrid API...")
                            from utils.simple_email_service import send_email_via_sendgrid_api
                            success = send_email_via_sendgrid_api(
                                ', '.join(msg.recipients), 
                                msg.subject, 
                                str(msg.html) if hasattr(msg, 'html') and msg.html else 'Email content',
                                app
                            )
                            if not success:
                                print("❌ SendGrid API failed, using simple fallback...")
                                from utils.simple_email_service import send_email_simple_fallback
                                success = send_email_simple_fallback(
                                    ', '.join(msg.recipients), 
                                    msg.subject, 
                                    str(msg.html) if hasattr(msg, 'html') and msg.html else 'Email content',
                                    app
                                )
                            if success:
                                print("✅ Email sent via final fallback")
                            else:
                                print("❌ All email methods failed in background thread")
        except Exception as e:
            print(f"❌ Background thread crashed: {e}")
    
    thread = threading.Thread(target=send_in_background)
    thread.daemon = True
    thread.start()
    print(f"🧵 Background thread started with ID: {thread.ident}")
    
    # Add a timeout to prevent hanging
    def timeout_handler():
        import time
        time.sleep(15)  # Wait 15 seconds
        if thread.is_alive():
            print("⏰ Background email thread timed out after 15 seconds")
    
    timeout_thread = threading.Thread(target=timeout_handler)
    timeout_thread.daemon = True
    timeout_thread.start()
    
    return True

def send_email_sync_with_fallback(mail, msg, app):
    """Send email synchronously with immediate fallback - returns quickly"""
    try:
        with app.app_context():
            # Try Flask-Mail with very short timeout
            import socket
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(5)  # Very short timeout
            
            try:
                mail.send(msg)
                print("Email sent successfully via Flask-Mail")
                return True
            except Exception as e:
                print(f"Flask-Mail failed quickly: {e}")
                print("🚀 Starting background email thread...")
                # Start background thread for fallback
                send_email_async_with_context(mail, msg, app)
                return True  # Return success immediately, let background handle it
            finally:
                socket.setdefaulttimeout(original_timeout)
                
    except Exception as e:
        print(f"Sync email sending failed: {e}")
        print("🚀 Starting background email thread...")
        # Start background thread for fallback
        send_email_async_with_context(mail, msg, app)
        return True  # Return success immediately

def try_direct_smtp_sending(msg, app):
    """Try direct SMTP sending with multiple providers"""
    try:
        with app.app_context():
            print("🔍 Trying direct SMTP providers...")
            # Try Gmail first
            print("📧 Attempting Gmail SMTP (port 587)...")
            if try_smtp_provider(msg, app, 'smtp.gmail.com', 587):
                return True
            
            # Try alternative providers
            providers = [
                ('smtp.sendgrid.net', 587),  # SendGrid (recommended for cloud)
                ('smtp.gmail.com', 465),  # Gmail SSL
                ('smtp.outlook.com', 587),  # Outlook
                ('smtp.mail.yahoo.com', 587),  # Yahoo
            ]
            
            for server, port in providers:
                print(f"📧 Attempting {server}:{port}...")
                if try_smtp_provider(msg, app, server, port):
                    return True
                    
        return False
    except Exception as e:
        print(f"Direct SMTP sending failed: {e}")
        return False

def try_smtp_provider(msg, app, server, port):
    """Try sending email with a specific SMTP provider"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Check if credentials are available
        username = app.config.get('MAIL_USERNAME')
        password = app.config.get('MAIL_PASSWORD')
        
        if not username or not password:
            print(f"❌ No email credentials configured for {server}:{port}")
            return False
            
        print(f"🔐 Using credentials: {username[:3]}***@{username.split('@')[1] if '@' in username else 'unknown'}")
        
        # Create email message
        email_msg = MIMEMultipart()
        email_msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        email_msg['To'] = ', '.join(msg.recipients)
        email_msg['Subject'] = msg.subject
        
        # Convert HTML to text
        if hasattr(msg, 'html') and msg.html:
            import re
            text_content = re.sub(r'<[^>]+>', '', str(msg.html))
            email_msg.attach(MIMEText(text_content, 'plain'))
        else:
            email_msg.attach(MIMEText('Email content', 'plain'))
        
        # Try to send with very short timeout
        with smtplib.SMTP(server, port, timeout=5) as smtp_server:
            if port == 465:
                # SSL connection
                smtp_server = smtplib.SMTP_SSL(server, port, timeout=5)
            else:
                # TLS connection
                smtp_server.starttls()
            
            smtp_server.login(username, password)
            smtp_server.send_message(email_msg)
            print(f"✅ Email sent successfully via {server}:{port}")
            return True
            
    except Exception as e:
        print(f"❌ SMTP {server}:{port} failed: {e}")
        return False
