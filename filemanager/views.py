import os
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View

from .models import Folder, File


@staff_member_required
def file_manager(request, folder_id=None):
    """Main file manager view."""
    current_folder = None
    breadcrumbs = []

    if folder_id:
        current_folder = get_object_or_404(Folder, pk=folder_id)
        breadcrumbs = current_folder.get_breadcrumbs()

    subfolders = Folder.objects.filter(parent=current_folder).prefetch_related('files', 'subfolders')
    files = File.objects.filter(folder=current_folder)

    return render(request, 'admin/filemanager/browser.html', {
        'current_folder': current_folder,
        'breadcrumbs': breadcrumbs,
        'subfolders': subfolders,
        'files': files,
        'title': 'File Manager',
        # Django admin context
        'has_permission': True,
        'site_header': 'Django Administration',
    })


@staff_member_required
@require_POST
def create_folder(request):
    name = request.POST.get('name', '').strip()
    parent_id = request.POST.get('parent_id') or None

    if not name:
        messages.error(request, 'Folder name cannot be empty.')
        return redirect_back(request, parent_id)

    parent = get_object_or_404(Folder, pk=parent_id) if parent_id else None

    if Folder.objects.filter(name=name, parent=parent).exists():
        messages.error(request, f'A folder named "{name}" already exists here.')
    else:
        Folder.objects.create(name=name, parent=parent)
        messages.success(request, f'Folder "{name}" created.')

    return redirect_back(request, parent_id)


@staff_member_required
@require_POST
def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, pk=folder_id)
    parent_id = folder.parent_id
    name = folder.name
    folder.delete()
    messages.success(request, f'Folder "{name}" and all its contents deleted.')
    return redirect_back(request, parent_id)


@staff_member_required
@require_POST
def upload_file(request):
    folder_id = request.POST.get('folder_id') or None
    folder = get_object_or_404(Folder, pk=folder_id) if folder_id else None

    uploaded_files = request.FILES.getlist('files')
    if not uploaded_files:
        messages.error(request, 'No files selected.')
        return redirect_back(request, folder_id)

    for f in uploaded_files:
        file_obj = File(
            name=f.name,
            file=f,
            folder=folder,
        )
        file_obj.save()

    messages.success(request, f'{len(uploaded_files)} file(s) uploaded successfully.')
    return redirect_back(request, folder_id)


@staff_member_required
@require_POST
def delete_file(request, file_id):
    file_obj = get_object_or_404(File, pk=file_id)
    folder_id = file_obj.folder_id
    name = file_obj.name

    # Delete physical file
    if file_obj.file and os.path.isfile(file_obj.file.path):
        os.remove(file_obj.file.path)
    file_obj.delete()

    messages.success(request, f'File "{name}" deleted.')
    return redirect_back(request, folder_id)


@staff_member_required
def file_detail_json(request, file_id):
    """Returns file metadata as JSON (for modal preview)."""
    file_obj = get_object_or_404(File, pk=file_id)
    data = {
        'id': file_obj.pk,
        'name': file_obj.name,
        'file_type': file_obj.file_type,
        'size': file_obj.human_size(),
        'uploaded_at': file_obj.uploaded_at.strftime('%Y-%m-%d %H:%M'),
        'url': file_obj.file.url,
        'folder': str(file_obj.folder) if file_obj.folder else 'Root',
    }
    return JsonResponse(data)


def redirect_back(request, folder_id=None):
    from django.urls import reverse
    if folder_id:
        return redirect(reverse('filemanager_browse_folder', args=[folder_id]))
    return redirect(reverse('filemanager_browse'))
