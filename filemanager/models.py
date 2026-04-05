import os
from django.db import models
from django.utils import timezone


class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='subfolders',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('name', 'parent')
        ordering = ['name']

    def __str__(self):
        return self.full_path

    @property
    def full_path(self):
        if self.parent:
            return f"{self.parent.full_path}/{self.name}"
        return self.name

    def get_breadcrumbs(self):
        """Returns list of (name, id) tuples from root to this folder."""
        crumbs = []
        folder = self
        while folder:
            crumbs.insert(0, (folder.name, folder.pk))
            folder = folder.parent
        return crumbs


def upload_to(instance, filename):
    folder_path = instance.folder.full_path if instance.folder else 'uncategorized'
    return os.path.join('filemanager', folder_path, filename)


class File(models.Model):
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('archive', 'Archive'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=upload_to)
    folder = models.ForeignKey(
        Folder,
        null=True,
        blank=True,
        related_name='files',
        on_delete=models.SET_NULL
    )
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='other')
    size = models.PositiveBigIntegerField(default=0)  # bytes
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.file:
            self.size = self.file.size
            ext = os.path.splitext(self.file.name)[1].lower()
            self.file_type = self._detect_type(ext)
            if not self.name:
                self.name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

    def _detect_type(self, ext):
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

    def human_size(self):
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
