from utils.extensions import db
from werkzeug.security import generate_password_hash
from models import User, RoomType, Room, GalleryImage, Booking
from PIL import Image
import os
from datetime import datetime, timedelta

def init_db(app):
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            # Create admin user
            admin = User(
                name='Administrator',
                email='admin@example.com',
                phone='+1234567890',
                password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                is_admin=True,
                verification_token=None  # Initialize verification_token as None
            )
            try:
                db.session.add(admin)
                db.session.commit()
                print("Admin user created successfully")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating admin user: {str(e)}")
        else:
            print("Admin user already exists")
        
        # Create gallery folder and sample images
        try:
            # Define gallery folder path
            gallery_folder = os.path.join('static', 'images', 'gallery')
            os.makedirs(gallery_folder, exist_ok=True)
            
            # Create sample images with different colors
            sample_images = [
                {
                    'filename': 'room1.jpg',
                    'size': (800, 600),
                    'color': (200, 150, 100),
                    'title': 'Luxury Room',
                    'description': 'Our spacious luxury room with ocean view',
                    'category': 'room'
                },
                {
                    'filename': 'dining1.jpg',
                    'size': (800, 600),
                    'color': (150, 100, 50),
                    'title': 'Fine Dining Restaurant',
                    'description': 'Experience exquisite cuisine in our restaurant',
                    'category': 'dining'
                },
                {
                    'filename': 'pool1.jpg',
                    'size': (800, 600),
                    'color': (50, 150, 200),
                    'title': 'Infinity Pool',
                    'description': 'Relax in our stunning infinity pool',
                    'category': 'pool'
                }
            ]
            
            # Create images and database entries
            for image_data in sample_images:
                # Create the image file
                img = Image.new('RGB', image_data['size'], image_data['color'])
                filepath = os.path.join(gallery_folder, image_data['filename'])
                img.save(filepath)
                print(f"Created {filepath}")
                
                # Create database entry
                gallery_image = GalleryImage(
                    filename=image_data['filename'],
                    title=image_data['title'],
                    description=image_data['description'],
                    category=image_data['category']
                )
                db.session.add(gallery_image)
            
            db.session.commit()
            print("Sample gallery images and database entries created successfully")
            
        except Exception as e:
            print(f"Error creating sample gallery: {str(e)}")
            db.session.rollback()
        
        try:
            # Add initial room types if they don't exist
            room_types = [
                RoomType(
                    name='Standard Room',
                    description='Comfortable room with basic amenities',
                    price_per_night=100.00
                ),
                RoomType(
                    name='Deluxe Room',
                    description='Spacious room with premium amenities',
                    price_per_night=200.00
                ),
                RoomType(
                    name='Suite',
                    description='Luxury suite with separate living area',
                    price_per_night=300.00
                )
            ]
            db.session.add_all(room_types)
            db.session.commit()
            print("Room types created successfully")

            # Add some rooms for each room type
            for room_type in room_types:
                for i in range(2):  # Add 2 rooms per type
                    room_number = f"{room_type.name[0]}{i+1}01"  # S101, S102, D101, D102, etc.
                    
                    # Check if room already exists
                    existing_room = Room.query.filter_by(room_number=room_number).first()
                    if not existing_room:
                        room = Room(
                            room_number=room_number,
                            floor=i+1,
                            room_type_id=room_type.id,
                            occupancy_limit=2 if room_type.name == 'Standard Room' else 4
                        )
                        db.session.add(room)
            
            db.session.commit()
            print("Rooms created successfully")
        except Exception as e:
            print(f"Error creating rooms: {str(e)}")
            db.session.rollback() 

def cleanup_expired_pending_bookings(expiry_minutes=60):
    """
    Set status to 'cancelled' for all pending bookings older than expiry_minutes.
    """
    expiry_time = datetime.utcnow() - timedelta(minutes=expiry_minutes)
    expired = Booking.query.filter(
        Booking.status == 'pending',
        Booking.created_at < expiry_time
    ).all()
    for booking in expired:
        booking.status = 'cancelled'
    if expired:
        db.session.commit()
    return len(expired) 