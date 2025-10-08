#!/bin/bash
sudo apt-get update
sudo apt-get install -y libjpeg-dev zlib1g-dev libcairo2 libcairo2-dev
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Initialize database if DATABASE_URL is set (production)
if [ ! -z "$DATABASE_URL" ]; then
    echo "Initializing database for production..."
    python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"
fi
