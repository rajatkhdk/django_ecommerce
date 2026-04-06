function confirmDeleteFolder(name) {
  return confirm(`Delete folder "${name}" and all its contents?`);
}

(function() {
  window.openFolderModal = function() {
    document.getElementById('folder-modal').classList.add('open');
    setTimeout(function() { document.getElementById('folder-name-input').focus(); }, 50);
  };
  window.closeFolderModal = function() {
    document.getElementById('folder-modal').classList.remove('open');
  };
  document.getElementById('folder-modal').addEventListener('click', function(e) {
    if (e.target === this) closeFolderModal();
  });

  document.getElementById('file-input').addEventListener('change', function() {
    if (this.files.length > 0) document.getElementById('upload-form').submit();
  });

  var zone = document.getElementById('drop-zone');
  zone.addEventListener('dragover', function(e) { e.preventDefault(); zone.classList.add('dragover'); });
  zone.addEventListener('dragleave', function() { zone.classList.remove('dragover'); });
  zone.addEventListener('drop', function(e) {
    e.preventDefault();
    zone.classList.remove('dragover');
    var files = e.dataTransfer.files;
    if (files.length) {
      try {
        var dt = new DataTransfer();
        for (var i = 0; i < files.length; i++) dt.items.add(files[i]);
        document.getElementById('file-input').files = dt.files;
      } catch(err) {}
      document.getElementById('upload-form').submit();
    }
  });

  window.previewFile = function(fileId) {
    document.getElementById('preview-modal').classList.add('open');
    document.getElementById('preview-content').innerHTML = 'Loading...';
    document.getElementById('preview-title').textContent = 'Loading...';
    document.getElementById('preview-download').href = '#';

    fetch('/admin/filemanager/file/' + fileId + '/json/', {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(function(r) { if (!r.ok) throw new Error('err'); return r.json(); })
    .then(function(data) {
      document.getElementById('preview-title').textContent = data.name;
      document.getElementById('preview-download').href = data.url;
      var html = '';
      if (data.file_type === 'image') html += '<img src="' + data.url + '" alt="' + data.name + '">';
      html += '<div class="fm-preview-meta">'
        + '<div><strong>Type:</strong> ' + data.file_type + '</div>'
        + '<div><strong>Size:</strong> ' + data.size + '</div>'
        + '<div><strong>Folder:</strong> ' + data.folder + '</div>'
        + '<div><strong>Uploaded:</strong> ' + data.uploaded_at + '</div>'
        + '</div>';
      document.getElementById('preview-content').innerHTML = html;
    })
    .catch(function() {
      document.getElementById('preview-content').innerHTML = '<span style="color:#dc3545;">Failed to load file info.</span>';
    });
  };

  window.closePreview = function() { document.getElementById('preview-modal').classList.remove('open'); };
  document.getElementById('preview-modal').addEventListener('click', function(e) {
    if (e.target === this) closePreview();
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') { closeFolderModal(); closePreview(); }
  });
})();