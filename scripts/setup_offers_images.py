import os
from PIL import Image

def create_sample_offer_images():
    # Define the offers folder path
    offers_folder = os.path.join('static', 'images', 'offers')
    os.makedirs(offers_folder, exist_ok=True)
    
    # Create sample images with different colors for each offer
    sample_images = [
        ('weekend-getaway.jpg', (800, 533), (120, 160, 200)),  # Blue-ish for weekend
        ('romantic-escape.jpg', (800, 533), (200, 150, 160)),  # Pink-ish for romantic
        ('family-fun.jpg', (800, 533), (150, 200, 150)),       # Green-ish for family
    ]
    
    for filename, size, color in sample_images:
        img = Image.new('RGB', size, color)
        filepath = os.path.join(offers_folder, filename)
        img.save(filepath)
        print(f"Created {filepath}")

if __name__ == "__main__":
    create_sample_offer_images() 