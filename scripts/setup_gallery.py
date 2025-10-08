import os
import shutil
from PIL import Image

def create_sample_gallery_images():
    # Define the gallery folder path
    gallery_folder = os.path.join('static', 'images', 'gallery')
    os.makedirs(gallery_folder, exist_ok=True)
    
    # Create sample images
    sample_images = [
        ('room1.jpg', (800, 600), (200, 150, 100)),  # Brown room
        ('dining1.jpg', (800, 600), (150, 100, 50)), # Dark dining room
        ('pool1.jpg', (800, 600), (50, 150, 200)),   # Blue pool
    ]
    
    for filename, size, color in sample_images:
        img = Image.new('RGB', size, color)
        filepath = os.path.join(gallery_folder, filename)
        img.save(filepath)
        print(f"Created {filepath}")

if __name__ == "__main__":
    create_sample_gallery_images() 