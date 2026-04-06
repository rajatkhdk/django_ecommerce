from django.urls import path
from . import views

# These are mounted under /admin/ via admin.py autodiscovery
urlpatterns = [
    path('filemanager/', views.file_manager, name='filemanager_browse'),
    path('filemanager/folder/<int:folder_id>/', views.file_manager, name='filemanager_browse_folder'),
    path('filemanager/folder/create/', views.create_folder, name='filemanager_create_folder'),
    path('filemanager/folder/<int:folder_id>/delete/', views.delete_folder, name='filemanager_delete_folder'),
    path('filemanager/file/upload/', views.upload_file, name='filemanager_upload_file'),
    path('filemanager/file/<int:file_id>/delete/', views.delete_file, name='filemanager_delete_file'),
    path('filemanager/file/<int:file_id>/json/', views.file_detail_json, name='filemanager_file_detail'),
]
