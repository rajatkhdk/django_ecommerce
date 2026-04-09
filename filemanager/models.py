# import os
# from django.db import models



# def upload_to(instance, filename):
#     folder_path = instance.folder.full_path if instance.folder else 'uncategorized'
#     return os.path.join('filemanager', folder_path, filename)


# class File(models.Model):
#     file = models.FileField(upload_to=upload_to)