import os
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.utils.decorators import method_decorator
import shutil
from .utils import get_thumbnail_url

BASE_DIR = os.path.join(settings.MEDIA_ROOT, 'filemanager').replace("\\", "/")

def human_readable_size(size):
    for unit in ['B','KB','MB','GB','TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

def get_folder_contents(abs_path,folder_path=""):
    subfolders = []
    files = []

    for entry in os.listdir(abs_path):
        full_path = os.path.join(abs_path, entry)
        # IMPORTANT: skip thumbnails folder (prevents recursion loop)
        if os.path.isdir(full_path) and entry == "thumbnails":
            continue

        relative_path = os.path.join(folder_path, entry).replace("\\", "/")
        
        if os.path.isdir(full_path):
            subfolders.append({
                'name': entry,
                'path': relative_path,
                'created_at': os.path.getctime(full_path),
            })
        else:
            url = settings.MEDIA_URL + 'filemanager/' + relative_path
            thumbnail = get_thumbnail_url(relative_path)
            files.append({
                'name': entry,
                'size': os.path.getsize(full_path),
                'human_size': human_readable_size(os.path.getsize(full_path)),
                'file_type': detect_file_type(entry),
                'path': relative_path,
                'created_at': os.path.getctime(full_path),
                'thumbnail': thumbnail,
                'url': url,
            })
    return subfolders, files

def detect_file_type(filename):
    ext = os.path.splitext(filename)[1].lower()
    images = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico', '.bmp', '.jfif'}
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

def list_folder(folder_path, search_query=None):
    base_path = os.path.join(BASE_DIR, folder_path).replace("\\", "/")
    # items = os.listdir(base_path)

    folders = []
    files = []

    for root, dirs, filenames in os.walk(base_path):
        
        rel_root = os.path.relpath(root, BASE_DIR).replace("\\", "/")

        if rel_root == ".":
            rel_root = ""

        for d in dirs:
            if search_query and search_query.lower() not in d.lower():
                continue

            full_path = os.path.join(root, d).replace("\\", "/")
            rel_path = os.path.join(rel_root, d).replace("\\", "/")

            folders.append({
                'name': d,
                'path': rel_path,
                'url': f'media/filemanager/{rel_path}',
                'created_at': os.path.getctime(full_path)
            })
        for f in filenames:
            if search_query and search_query.lower() not in f.lower():
                continue

            full_path = os.path.join(root, f).replace("\\", "/")
            rel_path =  os.path.join(rel_root, f).replace("\\", "/")

            files.append({
                'name': f,
                'path': rel_path,
                'url': f'media/filemanager/{rel_path}',
                'size': os.path.getsize(full_path),
                'created_at': os.path.getctime(full_path),
                'human_size': human_readable_size(os.path.getsize(full_path)),
                'file_type': detect_file_type(f),
            })

    
    # print(f"Inside function list_folder: \n Folders: {folders}, \nfiles: {files}, \nsearch_query: {search_query}")
    return folders, files

def sort_items(folders, files, sort_by='name', order='asc'):
    # print(f"Inside function sort_items: \n")
    reverse = (order == 'desc')
    if sort_by == 'name':
        folders.sort(key=lambda x: x['name'].lower(), reverse=reverse)
        files.sort(key=lambda x: x['name'].lower(), reverse=reverse)
    elif sort_by == 'size':
        files.sort(key=lambda x: x['size'], reverse=reverse)
    elif sort_by == 'date':
        folders.sort(key=lambda x: x['created_at'], reverse=reverse)
        files.sort(key=lambda x: x['created_at'], reverse=reverse)

    # print(f"Folders: {folders}, \nfiles: {files}, \nsort_by: {sort_by}, \norder: {order}")
    return folders, files

# def create_image_thumbnail(file_path, thumb_path, size=(150,150)):
#     try:
#         img = Image.open(file_path)
#         img.thumbnail(size)
#         img.save(thumb_path)
#         return thumb_path
#     except Exception as e:
#         print("Thumbnail creation failed:",e)
#         return None

@staff_member_required
def file_manager1(request, folder_path=""):
    print("file_manager_1 called")

    picker_mode = request.GET.get('picker', '0') == '1'

    search_query = request.GET.get('q', '').strip()

    current_folder = os.path.join(BASE_DIR, folder_path)

    if not os.path.exists(current_folder) or not os.path.isdir(current_folder):
        # Fallback to root
        current_folder = BASE_DIR
        folder_path = ""

    breadcrumbs = get_breadcrumbs_from_path(folder_path)
    subfolders, files = get_folder_contents(current_folder, folder_path)
    
    # get sorting params
    sort_by = request.GET.get('sort_by', 'name')
    order = request.GET.get('order', 'asc')

    # print(f"Sorting by: {sort_by}, order: {order}")
    if search_query:
        subfolders, files = list_folder(folder_path, search_query)

    subfolders, files = sort_items(subfolders, files, sort_by, order)

    

    # # apply sorting
    # subfolders, files = sort_items(subfolders, files, sort_by, order)

    # print(f"Inside file_manager1: \ncurrent_folder: {folder_path}, breadcrumbs: {breadcrumbs}, subfolders: {subfolders}, files: {files}, title: 'File Manager', has_permission: True, site_header: 'Django Administration'")

    # print(f"current_folder: {folder_path}, breadcrumbs: {breadcrumbs}, subfolders: {subfolders}, files: {files}, title: 'File Manager', has_permission: True, site_header: 'Django Administration'")

    # print(f"Inside filemanager: \nsearch_query: {search_query}")
    # print(f"searxh_folder: {search_folder} and search_files: {search_files}")

    # print("Files: ",files)

    return render(request, 'admin/filemanager/browser_1.html',{
        'current_folder': folder_path,
        'breadcrumbs': breadcrumbs,
        'subfolders': subfolders,
        'files': files,
        'picker_mode': picker_mode,
        # 'search_folder': search_folder,
        # 'search_files': search_files,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'title': 'File Manager',
        'has_permission': True,
        'site_header': 'Django Administration',
    })

@staff_member_required
@require_POST
def upload_file_fs(request):
    print("upload_file_fs called")
    # print("request in upload file : ", request)
    # print("POST data:", request.POST)
    # print("FILES:", request.FILES)
    folder_path = request.POST.get('folder_path','') # relative path
    current_folder = os.path.join(BASE_DIR, folder_path)
    os.makedirs(current_folder, exist_ok=True)

    uploaded_files = request.FILES.getlist('files')
    if not uploaded_files:
        messages.error(request, 'No files selected.')
        return redirect('filemanager_browse_folder_1', folder_path=folder_path)
    
    for f in uploaded_files:
        file_path = os.path.join(current_folder, f.name)
        with open(file_path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    messages.success(request, f'{len(uploaded_files)} file(s) uploaded successfully.')
    # return redirect('filemanager_browse_folder_1', folder_path=folder_path)
    if folder_path:
        return redirect('filemanager_browse_folder_1', folder_path=folder_path)
    else:
        return redirect('filemanager_browse_1')

@staff_member_required
@require_POST
def rename_item_fs(request):
    old_path = request.POST.get('old_path')
    new_name = request.POST.get('new_name')

    # print(f"old path: {old_path} \n new_path: {new_name}")

    name, ext = os.path.splitext(old_path)

    if os.path.isfile(old_path) and '.' not in new_name:
        new_name += ext

    if not old_path or not new_name:
        messages.error(request, "Invalid rename request.")
        return redirect(request.META.get('HTTP_REFERER', 'filemanager_browse_1'))
    
    # base_dir = os.path.dirname(old_path)
    # new_path = os.path.join(base_dir, new_name)

    if old_path and new_name:
        # Make absolute paths
        abs_old_path = os.path.join(BASE_DIR, old_path)
        abs_new_path = os.path.join(os.path.dirname(abs_old_path), new_name)

        # print("old_path:", abs_old_path)
        # print("new_path:", abs_new_path)

    # print(f"old_path: {old_path} \n new_path: {new_path}")

    try:
        os.rename(abs_old_path, abs_new_path)
        messages.success(request, f'Renamed to "{new_name}"')
    except Exception as e:
        messages.error(request, f'Error renaming: {str(e)}')

    return redirect(request.META.get('HTTP_REFERER', 'filemanager_browse_1'))


@staff_member_required
@require_POST
def delete_folder_fs(request, folder_path):
    print("delete_folder_fs called")
    BASE_DIR = os.path.join(settings.MEDIA_ROOT, 'filemanager')
    target_path = os.path.normpath(os.path.join(BASE_DIR, folder_path))

    # SECURITY CHECK (VERY IMPORTANT)
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
    # if parent_path == "":
    #     return redirect('filemanager_browse_1')

    messages.success(request, f'Folder "{folder_name}" and all its contents deleted.')
    if parent_path:
        return redirect('filemanager_browse_folder_1', folder_path=parent_path)
    else:
        return redirect('filemanager_browse_1')

@staff_member_required
@require_POST
def delete_file_fs(request, file_path):
    print("delete_file_fs called")
    base_dir = os.path.join(settings.MEDIA_ROOT, 'filemanager')
    target_path = os.path.normpath(os.path.join(base_dir, file_path))

    # SECURITY CHECK
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
    print("file_detail_json_fs called")
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
        'human_size': human_readable_size(os.path.getsize(full_path)),
        'uploaded_at': '',  # optional (you can skip or fake)
        'url': settings.MEDIA_URL + 'filemanager/' + file_path,
        'folder': os.path.dirname(file_path) or 'Root',
    }

    return JsonResponse(data)

def redirect_back(request, folder_path=None):
    from django.urls import reverse
    if folder_path:
        return redirect(reverse('filemanager_browse_folder_1', args=[folder_path]))
    return redirect(reverse('filemanager_browse_1'))

# @staff_member_required
@require_POST
def create_folder_fs(request):
    print("create_folder_fs called")
    base_dir = os.path.join(settings.MEDIA_ROOT, 'filemanager')

    # print(f"request : {request}")

    name = request.POST.get('name', '').strip()
    folder_path = request.POST.get('folder_path', '').strip()

    if not name:
        messages.error(request, 'Folder name cannot be empty.')
        if folder_path:
            return redirect('filemanager_browse_folder_1', folder_path=folder_path)
        return redirect('filemanager_browse_1')

    current_path = os.path.normpath(os.path.join(base_dir, folder_path))
    new_folder_path = os.path.join(current_path, name)

    # SECURITY CHECK
    if not current_path.startswith(base_dir):
        messages.error(request, "Invalid path.")
        return redirect('filemanager_browse_1')

    # Prevent duplicate folder
    if os.path.exists(new_folder_path):
        messages.error(request, f'Folder "{name}" already exists.')
    else:
        os.makedirs(new_folder_path)
        messages.success(request, f'Folder "{name}" created.')

    # Redirect back
    if folder_path:
        return redirect('filemanager_browse_folder_1', folder_path=folder_path)
    else:
        return redirect('filemanager_browse_1')