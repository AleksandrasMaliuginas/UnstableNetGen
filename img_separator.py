import os
import shutil
from PIL import Image

def move_images_with_size(source_folder, destination_folder, width, height):
    # Create destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # Iterate through files in source folder
    for filename in os.listdir(source_folder):
        filepath = os.path.join(source_folder, filename)
        # Check if file is an image
        if os.path.isfile(filepath) and any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            # Open image and get its dimensions
            with Image.open(filepath) as img:
                img_width, img_height = img.size
                # Check if dimensions match criteria
                if img_width == width and img_height == height:
                    # Move image to destination folder
                    shutil.copy(filepath, os.path.join(destination_folder, filename))
                    #print(f"Moved {filename} to {destination_folder}")

# Specify source and destination folders
source_folder = "pepeimg"
destination_folder = "zimages"

# Specify width and height criteria
width = 1920
height = 1080

# Call function to move images
move_images_with_size(source_folder, destination_folder, width, height)