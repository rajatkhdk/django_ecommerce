import os
from PIL import Image
from django.conf import settings
from django.http import JsonResponse
import shutil

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico', '.bmp', '.jfif']

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

def set_clipboard(request):
    """
    Stores selected files for copy/cut
    """
    items = request.POST.getlist('items[]')
    action = request.POST.get('action') # copy or cut

    if action not in ['copy', 'cut']:
        return JsonResponse({'error': 'Invalid action'}, status=400)
    
    request.session['clipboard'] = {
        'action': action,
        'items': items
    }
    request.session.modified = True

    return JsonResponse({'status': 'success'})

# def get_clipboard(request):
#     return JsonResponse(request.session.get('clipboard', {}))

def safe_join(base, path):
    final = os.path.normpath(os.path.join(base, path))
    base = os.path.normpath(base)
    
    if not final.startswith(base):
        raise Exception("Unsafe path detected")
    return final

def paste_items(request):
    destination = request.POST.get('destination') # relative path

    clipboard = request.session.get('clipboard')

    if not clipboard:
        return JsonResponse({'error': 'Clipboard empty'}, status=400)
    
    action = clipboard['action']
    items = clipboard['items']

    base = os.path.join(settings.MEDIA_ROOT, 'filemanager')
    dest_path = os.path.join(base, destination)

    os.makedirs(dest_path, exist_ok=True)

    for item in items:
        src = os.path.join(base, item)
        dst = os.path.join(dest_path, os.path.basename(item))

        # copy
        if action == 'copy':
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)

        # cut (move)
        elif action == 'cut':
            request.session['clipboard'] = None

    return JsonResponse({'status': 'success'})
    
