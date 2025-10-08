from app import app, db
from models import GalleryImage
from PIL import Image
import os

def init_gallery():
    with app.app_context():
        # Clear existing gallery images
        GalleryImage.query.delete()
        db.session.commit()
        
        # Create gallery folder
        gallery_folder = os.path.join('static', 'images', 'gallery')
        os.makedirs(gallery_folder, exist_ok=True)
        
        # Sample images data
        sample_images = [
            {
                'filename': 'room1.jpg',
                'size': (800, 600),
                'color': (200, 150, 100),
                'title': 'Luxury Suite',
                'description': 'Our spacious luxury suite with ocean view',
                'category': 'room'
            },
            {
                'filename': 'dining1.jpg',
                'size': (800, 600),
                'color': (150, 100, 50),
                'title': 'Restaurant',
                'description': 'Fine dining experience',
                'category': 'dining'
            },
            {
                'filename': 'pool1.jpg',
                'size': (800, 600),
                'color': (50, 150, 200),
                'title': 'Swimming Pool',
                'description': 'Infinity pool with ocean view',
                'category': 'pool'
            }
        ]
        
        for image_data in sample_images:
            # Create image file
            img = Image.new('RGB', image_data['size'], image_data['color'])
            filepath = os.path.join(gallery_folder, image_data['filename'])
            img.save(filepath)
            print(f"Created image: {filepath}")
            
            # Create database entry
            gallery_image = GalleryImage(
                filename=image_data['filename'],
                title=image_data['title'],
                description=image_data['description'],
                category=image_data['category']
            )
            db.session.add(gallery_image)
        
        db.session.commit()
        print("Gallery initialized successfully!")

if __name__ == "__main__":
    init_gallery() 