#!/usr/bin/env python3
"""
Health check script for debugging Render deployment issues
"""

import os
import sys
from app import create_app, db

def health_check():
    """Perform health checks"""
    print("🔍 Starting health check...")
    
    try:
        # Check environment variables
        print("\n📋 Environment Variables:")
        print(f"DATABASE_URL: {'✅ Set' if os.getenv('DATABASE_URL') else '❌ Not set'}")
        print(f"MAIL_USERNAME: {'✅ Set' if os.getenv('MAIL_USERNAME') else '❌ Not set'}")
        print(f"MAIL_PASSWORD: {'✅ Set' if os.getenv('MAIL_PASSWORD') else '❌ Not set'}")
        print(f"FLASK_SECRET_KEY: {'✅ Set' if os.getenv('FLASK_SECRET_KEY') else '❌ Not set'}")
        
        # Test app creation
        print("\n🏗️ Testing app creation...")
        app = create_app()
        print("✅ App created successfully")
        
        # Test database connection
        print("\n🗄️ Testing database connection...")
        with app.app_context():
            try:
                # Test basic connection
                db.engine.execute('SELECT 1')
                print("✅ Database connection successful")
                
                # Check if tables exist
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"✅ Tables found: {', '.join(tables) if tables else 'No tables found'}")
                
                # Test User table specifically
                if 'user' in tables:
                    user_count = db.session.execute('SELECT COUNT(*) FROM "user"').scalar()
                    print(f"✅ User table accessible, {user_count} users found")
                else:
                    print("❌ User table not found")
                    
            except Exception as e:
                print(f"❌ Database error: {e}")
                return False
        
        # Test email configuration
        print("\n📧 Testing email configuration...")
        if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
            print("✅ Email configuration looks good")
        else:
            print("❌ Email configuration missing")
        
        print("\n✅ Health check completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = health_check()
    sys.exit(0 if success else 1)
