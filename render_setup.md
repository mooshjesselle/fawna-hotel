# Render Deployment Setup

## Environment Variables to Set on Render

1. **DATABASE_URL** - This is automatically provided by Render when you add a PostgreSQL database
2. **FLASK_SECRET_KEY** - Set a strong secret key for your Flask app
3. **MAIL_USERNAME** - Your Gmail address for sending emails
4. **MAIL_PASSWORD** - Your Gmail app password
5. **SENDGRID_API_KEY** - Your SendGrid API key (recommended for production)
6. **SENDGRID_FROM_EMAIL** - Email address to send from (use a verified domain, e.g., noreply@yourdomain.com)
7. **SENDGRID_FROM_NAME** - Display name for emails (e.g., "FAWNA Hotel")
8. **FOOD_SERVICE_IPV4** - IP address for food service (if applicable)
9. **VAPID_PUBLIC_KEY** - For web push notifications (optional)
10. **VAPID_PRIVATE_KEY** - For web push notifications (optional)
11. **VAPID_SUBJECT** - For web push notifications (optional)

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

## Email Delivery Issues (DMARC) - FAWNA Hotel Solution

**Problem**: Emails going to spam due to DMARC policy failures when using Gmail addresses with SendGrid.

**Solution for FAWNA Hotel**: Use verified domain `fawnahotel.fwh.is` with proper DNS configuration.

### Step 1: Domain Authentication in SendGrid
1. Go to SendGrid Dashboard > Settings > Sender Authentication
2. Click "Authenticate Your Domain"
3. Enter domain: `fawnahotel.fwh.is`
4. Add the DNS records SendGrid provides to your domain provider
5. Verify domain authentication

### Step 2: Update SendGrid Sender Configuration
1. Go to SendGrid Dashboard > Settings > Sender Authentication
2. Edit your existing sender "Fawna Hotel"
3. Update the configuration:
   - **From**: `noreply@fawnahotel.fwh.is`
   - **Reply**: `fawnahotel@gmail.com`
   - **Nickname**: `FAWNA Hotel`

### Step 3: Update Environment Variables
Set these in your Render dashboard:
- `SENDGRID_FROM_EMAIL=noreply@fawnahotel.fwh.is`
- `SENDGRID_FROM_NAME=FAWNA Hotel`
- `SENDGRID_REPLY_TO=fawnahotel@gmail.com`
- `SENDGRID_API_KEY=your_sendgrid_api_key`

**Result**: 
- ✅ Emails sent FROM: `noreply@fawnahotel.fwh.is` (verified domain)
- ✅ Replies go TO: `fawnahotel@gmail.com`
- ✅ DMARC passes, emails go to inbox instead of spam!
- ✅ **Professional hotel domain** appearance

## Notes
- Make sure to add a PostgreSQL database to your Render service
- The app will automatically use PostgreSQL in production and SQLite in development
- All MySQL dependencies have been removed from requirements.txt
- **Important**: Never use Gmail addresses (`@gmail.com`) as the sender when using SendGrid to avoid DMARC failures
