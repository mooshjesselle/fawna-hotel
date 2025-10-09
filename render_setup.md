# Render Deployment Setup

## Environment Variables to Set on Render

1. **DATABASE_URL** - This is automatically provided by Render when you add a PostgreSQL database
2. **FLASK_SECRET_KEY** - Set a strong secret key for your Flask app
3. **RESEND_API_KEY** - Resend API key for sending emails via HTTPS
4. **EMAIL_FROM** - Email sender, e.g. "FAWNA Hotel <no-reply@yourdomain.com>"
5. (Optional for local dev) **MAIL_USERNAME** and **MAIL_PASSWORD** if testing SMTP locally
6. **FOOD_SERVICE_IPV4** - IP address for food service (if applicable)
7. **VAPID_PUBLIC_KEY** - For web push notifications (optional)
8. **VAPID_PRIVATE_KEY** - For web push notifications (optional)
9. **VAPID_SUBJECT** - For web push notifications (optional)

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
- Render web services block outbound SMTP (25/465/587). This app uses Resend HTTP API in production and falls back to SMTP locally.
- Make sure to add a PostgreSQL database to your Render service
- The app will automatically use PostgreSQL in production and SQLite in development
- All MySQL dependencies have been removed from requirements.txt
