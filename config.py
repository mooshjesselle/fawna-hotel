import os
from dotenv import load_dotenv

load_dotenv()  # Ensure .env is loaded before anything else
print("DEBUG: os.getenv('FOOD_SERVICE_IPV4') =", os.getenv('FOOD_SERVICE_IPV4'))

class Config:
    # Email Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')

    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
    
    # Database Configuration
    # Use PostgreSQL for production (Render), SQLite for development
    if os.getenv('DATABASE_URL'):
        # Production database (Render provides DATABASE_URL)
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    else:
        # Development database
        SQLALCHEMY_DATABASE_URI = 'sqlite:///hotel.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Timezone Configuration
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Manila')  # Default to Asia/Manila time 

    # Food Service IPv4 Address
    # Update your .env file with: FOOD_SERVICE_IPV4=192.168.0.104
    FOOD_SERVICE_IPV4 = os.getenv('FOOD_SERVICE_IPV4')
    print("DEBUG: Config.FOOD_SERVICE_IPV4 =", FOOD_SERVICE_IPV4)
    if not FOOD_SERVICE_IPV4:
        raise RuntimeError('FOOD_SERVICE_IPV4 must be set in your .env file!') 

    # Upload/Files Configuration
    # Enforce a 5MB max upload size for ID images
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    # Restrict uploaded ID images to common formats
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    # Web Push (placeholders; set via environment for production)
    VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY', '')
    VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY', '')
    VAPID_CLAIMS = {
        "sub": os.getenv('VAPID_SUBJECT', 'mailto:admin@example.com')
    }