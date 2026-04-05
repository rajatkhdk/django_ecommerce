# Django File Manager — Setup Guide

A zero-dependency custom file manager for Django Admin.
No django-filer, no third-party packages.

---

## 1. Copy the App

Copy the `filemanager/` folder into your Django project root (next to `manage.py`).

```
myproject/
├── manage.py
├── myproject/
│   ├── settings.py
│   └── urls.py        ← edit this
└── filemanager/       ← add this
```

---

## 2. Add to INSTALLED_APPS

In `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'filemanager',
]
```

---

## 3. Configure Media Files

In `settings.py`:

```python
import os

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

In `urls.py` (your project-level urls, NOT the app):

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # ... your other urls
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

> ⚠️ The `static(...)` line is for development only.
> In production, serve /media/ via nginx or S3.

---

## 4. Run Migrations

```bash
python manage.py migrate
```

---

## 5. Access the File Manager

Log in to Django Admin, then visit:

```
http://localhost:8000/admin/filemanager/
```

Or add a link to your admin sidebar via a custom `admin/base_site.html` override:

```html
{# templates/admin/base_site.html #}
{% extends "admin/base.html" %}
{% block nav-global %}
  <a href="/admin/filemanager/" style="color:white;padding:8px;display:block;">📁 File Manager</a>
{% endblock %}
```

---

## Features

| Feature | Status |
|---|---|
| Create nested folders | ✅ |
| Delete folders (recursive) | ✅ |
| Upload multiple files | ✅ |
| Drag & drop upload | ✅ |
| Browse files by folder | ✅ |
| Delete individual files | ✅ |
| File type icons (image/doc/video/audio/archive) | ✅ |
| Image preview modal | ✅ |
| File metadata (size, date, type) | ✅ |
| Breadcrumb navigation | ✅ |
| Zero extra packages | ✅ |

---

## File Storage

Uploaded files are saved under:

```
media/filemanager/<folder-path>/<filename>
```

For example, a file in folder `photos/2024` goes to:
```
media/filemanager/photos/2024/my-image.jpg
```

---

## Production Notes

- For production, consider using `django-storages` + S3 for file storage
- The `upload_to` function in `models.py` can be swapped to point at S3
- Add `FILE_UPLOAD_MAX_MEMORY_SIZE` in settings to limit upload size:

```python
# settings.py
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB
```
