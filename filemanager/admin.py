from django.contrib import admin
from django.urls import path
from .models import Folder, File
from . import views


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_at')
    search_fields = ('name',)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'folder', 'file_type', 'size', 'uploaded_at')
    list_filter = ('file_type',)
    search_fields = ('name',)
    readonly_fields = ('size', 'file_type', 'uploaded_at')


# Inject the file manager URLs into the admin site
# This approach adds custom URLs directly into the admin namespace
_original_get_urls = admin.site.__class__.get_urls

def get_urls(self):
    from django.urls import path
    from filemanager import views as fm_views

    custom_urls = [
        path('filemanager/', fm_views.file_manager, name='filemanager_browse'),
        path('filemanager/folder/<int:folder_id>/', fm_views.file_manager, name='filemanager_browse_folder'),
        path('filemanager/folder/create/', fm_views.create_folder, name='filemanager_create_folder'),
        path('filemanager/folder/<int:folder_id>/delete/', fm_views.delete_folder, name='filemanager_delete_folder'),
        path('filemanager/file/upload/', fm_views.upload_file, name='filemanager_upload_file'),
        path('filemanager/file/<int:file_id>/delete/', fm_views.delete_file, name='filemanager_delete_file'),
        path('filemanager/file/<int:file_id>/json/', fm_views.file_detail_json, name='filemanager_file_detail'),
    ]
    return custom_urls + _original_get_urls(self)

admin.site.__class__.get_urls = get_urls
