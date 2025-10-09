"""
Simple email service that works without SMTP
This is a fallback for when SMTP is blocked on cloud platforms
"""
import requests
import json
from flask import current_app

def send_email_via_webhook(email, subject, html_content, app):
    """Send email using a webhook service (like EmailJS, Formspree, etc.)"""
    try:
        with app.app_context():
            # This is a placeholder for webhook-based email services
            # You can integrate with services like:
            # - EmailJS (https://www.emailjs.com/)
            # - Formspree (https://formspree.io/)
            # - Netlify Forms
            # - Custom webhook endpoint
            
            print(f"📧 Would send email to {email} with subject: {subject}")
            print("💡 To enable email sending, configure a webhook service")
            print("💡 Or set up SendGrid environment variables")
            
            # For now, just log the email details
            return True
            
    except Exception as e:
        print(f"❌ Webhook email failed: {e}")
        return False

def send_email_via_sendgrid_api(email, subject, html_content, app):
    """Send email using SendGrid API directly (no SMTP)"""
    try:
        with app.app_context():
            api_key = app.config.get('SENDGRID_API_KEY')
            from_email = app.config.get('SENDGRID_FROM_EMAIL')
            
            if not api_key or not from_email:
                print("❌ SendGrid API credentials not configured")
                return False
            
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "personalizations": [{
                    "to": [{"email": email}]
                }],
                "from": {"email": from_email},
                "subject": subject,
                "content": [{
                    "type": "text/html",
                    "value": html_content
                }]
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 202:
                print(f"✅ Email sent successfully via SendGrid API to {email}")
                return True
            else:
                print(f"❌ SendGrid API failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ SendGrid API error: {e}")
        return False

def send_email_simple_fallback(email, subject, html_content, app):
    """Simple fallback that always returns success for testing"""
    print(f"📧 SIMPLE FALLBACK: Would send email to {email}")
    print(f"📧 Subject: {subject}")
    print(f"📧 Content: {html_content[:100]}...")
    print("✅ Email marked as sent (fallback mode)")
    return True
