#!/usr/bin/env python3
"""
Database initialization script for Render deployment
"""

import os
import sys
from app import create_app, db
from models import User, Room, Booking, Comment, RoomType, Amenity, GalleryImage, HomePageImage, HomePageSettings, Promo, PromoRoom, PromoDiscount, Notification, IdVerification

def init_database():
    """Initialize database tables"""
    try:
        app = create_app()
        
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Created tables: {', '.join(tables)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
