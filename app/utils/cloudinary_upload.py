import cloudinary
import cloudinary.uploader
import os
from app.config import ( # Import credentials from app/config
    CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
)

# --- 1. Cloudinary SDK Initialization ---
# This configuration is loaded when the utility file is imported.
try:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True # Always use secure HTTPS URLs
    )
    print("Cloudinary SDK configured successfully.")
except Exception as e:
    print(f"ERROR: Could not configure Cloudinary SDK. Check environment variables: {e}")


def upload_event_image(image_file):
    """
    Uploads an image file to Cloudinary and applies optimization/resizing.

    :param image_file: The file object received from Flask (request.files['image']).
    :return: The secure URL of the uploaded image or None on failure.
    """
    if not image_file:
        return None
    
    # --- 2. Define Upload Options and Transformations ---
    # Non-functional requirement: Optimization and resizing logic
    try:
        # Use a folder structure for organization
        folder_name = "eventrift/event_posters"
        
        # Transformation options for optimization:
        # - width=1200: Max width of 1200px (good for modern web display)
        # - crop="limit": Ensures image fits within dimensions without cropping the subject
        # - quality="auto:best": Optimizes file size while maintaining high quality
        # - fetch_format="auto": Delivers the image in the most optimal format (e.g., webp)
        options = {
            "folder": folder_name,
            "resource_type": "image",
            "transformation": [
                {'width': 1200, 'crop': "limit"}, 
                {'quality': "auto:best", 'fetch_format': "auto"}
            ]
        }
        
        # --- 3. Perform the Upload ---
        upload_result = cloudinary.uploader.upload(
            image_file, 
            **options
        )
        
        # Check if the upload was successful and return the secure URL
        if upload_result and 'secure_url' in upload_result:
            print(f"Image uploaded successfully: {upload_result['secure_url']}")
            return upload_result['secure_url']
        else:
            print(f"Cloudinary upload failed: {upload_result}")
            return None

    except Exception as e:
        print(f"An error occurred during Cloudinary upload: {e}")
        return None
