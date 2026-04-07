import os
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
import shutil

BASE_DIR = os.path.join(settings.MEDIA_ROOT, 'filemanager')

def get_folder_contents(abs_path,folder_path=""):
    subfolders = []
    files = []

    for entry in os.listdir(abs_path):
        full_path = os.path.join(abs_path, entry)
        relative_path = os.path.join(folder_path, entry).replace("\\", "/")
        
        if os.path.isdir(full_path):
            subfolders.append({
                'name': entry,
                'path': relative_path,
            })
        else:
            files.append({
                'name': entry,
                'size': os.path.getsize(full_path),
                'file_type': detect_file_type(entry),
                'path': os.path.relpath(full_path, BASE_DIR),
            })
    return subfolders, files

def detect_file_type(filename):
    ext = os.path.splitext(filename)[1].lower()
    images = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico', '.bmp'}
    documents = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv', '.odt'}
    videos = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
    audio = {'.mp3', '.wav', '.ogg', '.flac', '.aac'}
    archives = {'.zip', '.tar', '.gz', '.rar', '.7z'}
    if ext in images: return 'image'
    if ext in documents: return 'document'
    if ext in videos: return 'video'
    if ext in audio: return 'audio'
    if ext in archives: return 'archive'
    return 'other'

def get_breadcrumbs_from_path(rel_path):
    """
    rel_path: relative path from BASE_DIR
    returns list of (name,path) tuples
    """
    parts = rel_path.strip("/").split("/") if rel_path else []
    crumbs = []
    for i in range(len(parts)):
        crumb_path = "/".join(parts[:i+1])
        crumbs.append((parts[i], crumb_path))
    return crumbs

@staff_member_required
def file_manager1(request, folder_path=""):
    current_folder = os.path.join(BASE_DIR, folder_path)

    if not os.path.exists(current_folder) or not os.path.isdir(current_folder):
        # Fallback to root
        current_folder = BASE_DIR
        folder_path = ""

    breadcrumbs = get_breadcrumbs_from_path(folder_path)
    subfolders, files = get_folder_contents(current_folder, folder_path)

    print(f"current_folder: {folder_path}, breadcrumbs: {breadcrumbs}, subfolders: {subfolders}, files: {files}, title: 'File Manager', has_permission: True, site_header: 'Django Administration'")

    return render(request, 'admin/filemanager/browser_1.html',{
        'current_folder': folder_path,
        'breadcrumbs': breadcrumbs,
        'subfolders': subfolders,
        'files': files,
        'title': 'File Manager',
        'has_permission': True,
        'site_header': 'Django Administration',
    })

@staff_member_required
@require_POST
def upload_file_fs(request):
    folder_path = request.POST.get('folder_path','') # relative path
    current_folder = os.path.join(BASE_DIR, folder_path)
    os.makedirs(current_folder, exist_ok=True)

    uploaded_files = request.FILES.getlist('files')
    if not uploaded_files:
        messages.error(request, 'No files selected.')
        return redirect('filemanager_browse_folder', folder_path=folder_path)
    
    for f in uploaded_files:
        file_path = os.path.join(current_folder, f.name)
        with open(file_path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    messages.success(request, f'{len(uploaded_files)} file(s) uploaded successfully.')
    return redirect('filemanager_browse_folder', folder_path=folder_path)

@staff_member_required
@require_POST
def delete_folder_fs(request, folder_path):
    BASE_DIR = os.path.join(settings.MEDIA_ROOT, 'filemanager')
    target_path = os.path.normpath(os.path.join(BASE_DIR, folder_path))

    # 🔒 SECURITY CHECK (VERY IMPORTANT)
    if not target_path.startswith(BASE_DIR):
        messages.error(request, "Invalid folder path.")
        return redirect('filemanager_browse_1')

    # Check if folder exists
    if not os.path.exists(target_path) or not os.path.isdir(target_path):
        messages.error(request, "Folder does not exist.")
        return redirect('filemanager_browse_1')

    # Get folder name
    folder_name = os.path.basename(target_path)

    # Delete folder and all contents
    shutil.rmtree(target_path)

    # Get parent path
    parent_path = os.path.dirname(folder_path)

    # Fix root case
    if parent_path == "":
        return redirect('filemanager_browse_1')

    messages.success(request, f'Folder "{folder_name}" and all its contents deleted.')
    return redirect('filemanager_browse_folder_1', folder_path=parent_path)

@staff_member_required
@require_POST
def delete_file_fs(request, file_path):
    base_dir = os.path.join(settings.MEDIA_ROOT, 'filemanager')
    target_path = os.path.normpath(os.path.join(base_dir, file_path))

    # 🔒 SECURITY CHECK
    if not target_path.startswith(base_dir):
        messages.error(request, "Invalid file path.")
        return redirect('filemanager_browse_1')

    if not os.path.exists(target_path) or not os.path.isfile(target_path):
        messages.error(request, "File does not exist.")
        return redirect('filemanager_browse_1')

    file_name = os.path.basename(target_path)

    # Delete file
    os.remove(target_path)

    # Redirect back to parent folder
    parent_path = os.path.dirname(file_path)

    messages.success(request, f'File "{file_name}" deleted.')

    if parent_path:
        return redirect('filemanager_browse_folder_1', folder_path=parent_path)
    else:
        return redirect('filemanager_browse_1')
    
@staff_member_required
def file_detail_json_fs(request, file_path):
    base_dir = os.path.join(settings.MEDIA_ROOT, 'filemanager')
    full_path = os.path.normpath(os.path.join(base_dir, file_path))

    # 🔒 SECURITY CHECK
    if not full_path.startswith(base_dir):
        return JsonResponse({'error': 'Invalid path'}, status=400)

    if not os.path.exists(full_path):
        return JsonResponse({'error': 'File not found'}, status=404)

    data = {
        'name': os.path.basename(full_path),
        'file_type': detect_file_type(full_path),
        'size': os.path.getsize(full_path),
        'uploaded_at': '',  # optional (you can skip or fake)
        'url': settings.MEDIA_URL + 'filemanager/' + file_path,
        'folder': os.path.dirname(file_path) or 'Root',
    }

    return JsonResponse(data)

def redirect_back(request, folder_path=None):
    from django.urls import reverse
    if folder_path:
        return redirect(reverse('filemanager_browser_folder_1', args=[folder_path]))
    return redirect(reverse('filemanager_browse_1'))

@staff_member_required
@require_POST
def create_folder_fs(request):
    base_dir = os.path.join(settings.MEDIA_ROOT, 'filemanager')

    name = request.POST.get('name', '').strip()
    folder_path = request.POST.get('folder_path', '').strip()

    if not name:
        messages.error(request, 'Folder name cannot be empty.')
        if folder_path:
            return redirect('filemanager_browse_folder_1', folder_path=folder_path)
        return redirect('filemanager_browse_1')

    current_path = os.path.normpath(os.path.join(base_dir, folder_path))
    new_folder_path = os.path.join(current_path, name)

    # 🔒 SECURITY CHECK
    if not current_path.startswith(base_dir):
        messages.error(request, "Invalid path.")
        return redirect('filemanager_browse_1')

    # ❌ Prevent duplicate folder
    if os.path.exists(new_folder_path):
        messages.error(request, f'Folder "{name}" already exists.')
    else:
        os.makedirs(new_folder_path)
        messages.success(request, f'Folder "{name}" created.')

    # 🔁 Redirect back
    if folder_path:
        return redirect('filemanager_browse_folder_1', folder_path=folder_path)
    else:
        return redirect('filemanager_browse_1')