from django.urls import path
from . import views1

# These are mounted under /admin/ via admin.py autodiscovery
urlpatterns = [
    path('filemanager/1/folder/<path:folder_path>/delete/', views1.delete_folder_fs, name='filemanager_delete_folder_1'),
    path('filemanager/1/folder/create/',views1.create_folder_fs,name='filemanager_create_folder_fs'),path('filemanager/1', views1.file_manager1,name='filemanager_browse_1'),
    
    path('filemanage/1/rename/', views1.rename_item_fs, name='filemanager_rename_fs'),
    
    path('filemanager/1/file/upload/', views1.upload_file_fs, name='filemanager_upload_file_fs'),
    path('filemanager/1/file/<path:file_path>/delete/', views1.delete_file_fs, name='filemanager_delete_file_fs'),
    
    path('filemanager/1/file/<path:file_path>/json/',views1.file_detail_json_fs, name='file_detail_json_fs'),
    path('filemanager/1/folder/<path:folder_path>/', views1.file_manager1, name='filemanager_browse_folder_1'),
]
