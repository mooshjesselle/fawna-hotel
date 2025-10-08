#!/bin/bash
sudo apt-get update
sudo apt-get install -y libjpeg-dev zlib1g-dev libcairo2 libcairo2-dev libpq-dev
pip install --upgrade pip setuptools wheel

# Install psycopg2-binary first to avoid compilation issues
pip install psycopg2-binary==2.9.10

# Install other requirements
pip install -r requirements.txt

# Initialize database if DATABASE_URL is set (production)
if [ ! -z "$DATABASE_URL" ]; then
    echo "Initializing database for production..."
    python -c "
import sys
sys.path.append('.')
from app import app, db
from models import User, Room, Booking, Comment, Amenity, HomePageImage, Promo, Notification
with app.app_context():
    try:
        db.create_all()
        print('Database tables created successfully')
    except Exception as e:
        print(f'Database initialization error: {e}')
        sys.exit(1)
"
fi
