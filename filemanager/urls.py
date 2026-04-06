from django.urls import path
from . import views
from . import views1

# These are mounted under /admin/ via admin.py autodiscovery
urlpatterns = [
    path('filemanager/', views.file_manager, name='filemanager_browse'),
    path('filemanager/folder/<int:folder_id>/', views.file_manager, name='filemanager_browse_folder'),
    path('filemanager/folder/create/', views.create_folder, name='filemanager_create_folder'),
    path('filemanager/folder/<int:folder_id>/delete/', views.delete_folder, name='filemanager_delete_folder'),
    path('filemanager/file/upload/', views.upload_file, name='filemanager_upload_file'),
    path('filemanager/file/<int:file_id>/delete/', views.delete_file, name='filemanager_delete_file'),
    path('filemanager/file/<int:file_id>/json/', views.file_detail_json, name='filemanager_file_detail'),


    path('filemanager/1', views1.file_manager1,name='filemanager_browse_1'),
    path('filemanager/1/folder/<path:folder_path>/', views1.file_manager1, name='filemanager_browser_folder_1'),
    path('filemanager/folder/<path:folder_path>/delete/', views1.delete_folder_fs, name='filemanager_delete_folder_1'),
    path('filemanager/file/upload/1', views1.upload_file_fs, name='filemanager_upload_file_fs'),
]
