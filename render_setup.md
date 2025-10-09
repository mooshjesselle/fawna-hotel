# Render Deployment Setup

## Environment Variables to Set on Render

### Required Variables:
1. **DATABASE_URL** - This is automatically provided by Render when you add a PostgreSQL database
2. **FLASK_SECRET_KEY** - Set a strong secret key for your Flask app
3. **FOOD_SERVICE_IPV4** - IP address for food service (if applicable)

### Email Configuration (Choose one option):

#### Option A: SendGrid (Recommended for Production)
4. **SENDGRID_API_KEY** - Your SendGrid API key
5. **SENDGRID_FROM_EMAIL** - Your verified sender email (e.g., fawnahotel@gmail.com)

#### Option B: Gmail (For Development)
4. **MAIL_USERNAME** or **SMTP_USERNAME** - Your Gmail address for sending emails
5. **MAIL_PASSWORD** or **SMTP_PASSWORD** - Your Gmail app password

### Optional Variables:
6. **VAPID_PUBLIC_KEY** - For web push notifications (optional)
7. **VAPID_PRIVATE_KEY** - For web push notifications (optional)
8. **VAPID_SUBJECT** - For web push notifications (optional)

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
