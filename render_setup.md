# Render Deployment Setup

## Environment Variables to Set on Render

1. **DATABASE_URL** - This is automatically provided by Render when you add a PostgreSQL database
2. **FLASK_SECRET_KEY** - Set a strong secret key for your Flask app
3. **MAIL_USERNAME** or **SMTP_USERNAME** - Your Gmail address for sending emails
4. **MAIL_PASSWORD** or **SMTP_PASSWORD** - Your Gmail app password
5. **FOOD_SERVICE_IPV4** - IP address for food service (if applicable)
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
