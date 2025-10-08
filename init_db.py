#!/usr/bin/env python3
"""
Database initialization script for Render deployment
Run this script to create all necessary database tables
"""

import os
import sys
from app import app, db
from models import User, Room, Booking, Comment, Amenity, HomePageImage, Promo, Notification

def init_database():
    """Initialize the database with all tables"""
    try:
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Created {len(tables)} tables: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Initializing FAWNA Hotel Database...")
    init_database()
    print("🎉 Database initialization complete!")
