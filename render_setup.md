# Render Deployment Setup

## Environment Variables to Set on Render

1. **DATABASE_URL** - This is automatically provided by Render when you add a PostgreSQL database
2. **FLASK_SECRET_KEY** - Set a strong secret key for your Flask app
3. **MAIL_USERNAME** - Your Gmail address for sending emails
4. **MAIL_PASSWORD** - Your Gmail app password
5. **FOOD_SERVICE_IPV4** - IP address for food service (if applicable)
6. **VAPID_PUBLIC_KEY** - For web push notifications (optional)
7. **VAPID_PRIVATE_KEY** - For web push notifications (optional)
8. **VAPID_SUBJECT** - For web push notifications (optional)

### Email Configuration (Required for Render)

**IMPORTANT**: Render blocks outbound SMTP connections to prevent spam. Gmail SMTP will not work on Render.

**Recommended Solution**: Use SendGrid (free tier available)

9. **SENDGRID_API_KEY** - Your SendGrid API key (get from sendgrid.com)
10. **SENDGRID_FROM_EMAIL** - Your verified sender email address for SendGrid

### SendGrid Setup Instructions

1. **Sign up for SendGrid**: Go to https://sendgrid.com and create a free account
2. **Create API Key**: 
   - Go to Settings → API Keys
   - Create a new API key with "Mail Send" permissions
   - Copy the API key
3. **Verify Sender Email**:
   - Go to Settings → Sender Authentication
   - Verify your email address
4. **Set Environment Variables on Render**:
   - `SENDGRID_API_KEY` = your API key
   - `SENDGRID_FROM_EMAIL` = your verified email

**Alternative**: You can also try:
- **MAIL_USERNAME** - Your Gmail address (may not work due to Render restrictions)
- **MAIL_PASSWORD** - Your Gmail app password (may not work due to Render restrictions)

## Build Command
```bash
./build.sh
```

## Start Command
```bash
gunicorn app:app
```

## Database Setup
The app will automatically create database tables on first run using Flask-SQLAlchemy's `create_all()` method.

## Notes
- Make sure to add a PostgreSQL database to your Render service
- The app will automatically use PostgreSQL in production and SQLite in development
- All MySQL dependencies have been removed from requirements.txt

## Email Configuration Notes
- The app now includes timeout handling and async email sending to prevent worker timeouts
- If Gmail SMTP continues to cause issues, consider using SendGrid as an alternative
- Email sending is now asynchronous to prevent blocking the main application thread
- The app includes fallback email sending methods for better reliability
