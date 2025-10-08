from flask import Flask
from app import create_app, db

"""
Migration script to add booking_id column to the notification table.
Run this script directly with: python migrations/add_notification_booking.py
"""

def run_migration():
    print("Starting migration to add booking_id to notification table...")
    
    # Create a Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Add booking_id column
            print("Adding booking_id column...")
            db.engine.execute('ALTER TABLE notification ADD COLUMN booking_id INT NULL')
            
            # Add foreign key constraint
            print("Adding foreign key constraint...")
            db.engine.execute('ALTER TABLE notification ADD CONSTRAINT fk_notification_booking FOREIGN KEY (booking_id) REFERENCES booking(id)')
            
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Migration failed: {e}")
            print("Note: If column already exists, you can ignore this error")

if __name__ == "__main__":
    run_migration() 