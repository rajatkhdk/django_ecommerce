import os
from PIL import Image
from django.conf import settings

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

def is_image(file_name):
    ext = os.path.splitext(file_name)[1].lower()
    return ext in IMAGE_EXTENSIONS

def get_thumbnail_url(relative_path):
    """
    relative_path: path relative to filemanager/
    example: 'folder1/image.jpg'
    """

    # Absolute original file path
    original_path = os.path.join(settings.MEDIA_ROOT, 'filemanager', relative_path)

    # If not image -> return None (use icon later)
    if not is_image(relative_path):
        return None
    
    # Thumbnail directory (inside same folder)
    folder = os.path.dirname(original_path)
    thumb_dir = os.path.join(folder, 'thumbnails')
    os.makedirs(thumb_dir, exist_ok=True)

    # Thumbnail file path
    filename = os.path.basename(original_path)
    thumb_path = os.path.join(thumb_dir, filename)

    # If thumbnail does Not exist -> create it
    if not os.path.exists(thumb_path):
        try:
            img = Image.open(original_path)
            img.thumbnail((100, 100))
            img.save(thumb_path)
        except Exception as e:
            print("Thumbnail error: e")
            return None
        
    # Convert thumbnail path → URL
    rel_thumb_path = os.path.relpath(thumb_path, settings.MEDIA_ROOT).replace("\\", "/")
    return settings.MEDIA_URL + rel_thumb_path