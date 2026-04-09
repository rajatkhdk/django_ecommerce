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

  var fileInput = document.getElementById('file-input');
  if (fileInput){
  fileInput.addEventListener('change', function() {
    if (this.files.length > 0) document.getElementById('upload-form').submit();
  });
}

  var zone = document.getElementById('drop-zone');
  if (zone){
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
}

  // console.log("Before previewFile definition");

  window.openRenameModal = function(path, name){
    console.log("Inside openRenameModal")
    const modal = document.getElementById('rename-modal');
    modal.classList.add('open');  // show
    document.getElementById('rename-old-path').value = path;
    document.getElementById('rename-input').value = name;
    document.getElementById('rename-input').focus();
}

  window.closeRenameModal = function() {
    console.log("Inside CloseRenameModal")
    document.getElementById('rename-modal').classList.remove('open'); // hide
}

  window.previewFile = function(filepath) {
    console.log("inside previewFile")
    document.getElementById('preview-modal').classList.add('open');
    document.getElementById('preview-content').innerHTML = 'Loading...';
    document.getElementById('preview-title').textContent = 'Loading...';
    document.getElementById('preview-download').href = '#';

    // console.log(filepath)

    fetch('/admin/filemanager/1/file/' + encodeURIComponent(filepath) + '/json/', {
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
        // + '<div><strong>Size:</strong> ' + data.size + '</div>'
        + '<div><strong>Size:</strong> ' + data.human_size + '</div>'
        + '<div><strong>Folder:</strong> ' + data.folder + '</div>'
        + '<div><strong>Uploaded:</strong> ' + data.uploaded_at + '</div>'
        + '</div>';
      document.getElementById('preview-content').innerHTML = html;
    })
    .catch(function() {
      document.getElementById('preview-content').innerHTML = '<span style="color:#dc3545;">Failed to load file info.</span>';
    });
  };

  // console.log("Before selectFile definition");

  window.selectFile = function(filePath) {

    console.log("Inside selectFile", filePath);

    const fullUrl = "/media/filemanager/" + filePath;

    console.log("Inside selectFile",fullUrl)

    if (window.opener && window.opener.setSelectedFile){
      window.opener.setSelectedFile(filePath, fullUrl);
      window.close();
    }else{
      alert("No parent window found.")
    }
    };

//   // Check for picker mode via query param
// function getQueryParam(param) {
//   const url = new URL(window.location.href);
//   return url.searchParams.get(param);
// }

// window.previewFile = function(filepath, isPicker=false) {
//   // Automatically enable picker if query param exists
//   const pickerParam = getQueryParam('picker');
//   if(pickerParam === '1') isPicker = true;

//   document.getElementById('preview-modal').classList.add('open');
//   document.getElementById('preview-content').innerHTML = 'Loading...';
//   document.getElementById('preview-title').textContent = 'Loading...';

//   // reset buttons
//   document.getElementById('preview-open').style.display = 'inline-block';
//   const selectBtn = document.querySelector('.fm-modal-actions button[onclick="selectFileForForm()"]');
//   if(selectBtn) selectBtn.style.display = isPicker ? 'inline-block' : 'none';

//   fetch('/admin/filemanager/1/file/' + encodeURIComponent(filepath) + '/json/', {
//     headers: { 'X-Requested-With': 'XMLHttpRequest' }
//   })
//   .then(r => { if(!r.ok) throw new Error('err'); return r.json(); })
//   .then(data => {
//     document.getElementById('preview-title').textContent = data.name;
//     document.getElementById('preview-open').href = data.url;

//     var html = '';
//     if(data.file_type === 'image') html += '<img src="' + data.url + '" alt="' + data.name + '" style="max-width:100%;">';
//     html += '<div class="fm-preview-meta">'
//       + '<div><strong>Type:</strong> ' + data.file_type + '</div>'
//       + '<div><strong>Size:</strong> ' + data.size + '</div>'
//       + '<div><strong>Folder:</strong> ' + data.folder + '</div>'
//       + '<div><strong>Uploaded:</strong> ' + data.uploaded_at + '</div>'
//       + '</div>';
//     document.getElementById('preview-content').innerHTML = html;

//     // store URL globally for select
//     window._previewFileUrl = data.url;
//   })
//   .catch(() => {
//     document.getElementById('preview-content').innerHTML = '<span style="color:#dc3545;">Failed to load file info.</span>';
//   });
// };

//   window.selectFileForForm = function() {
//   const input = window.opener
//     ? window.opener.document.querySelector('#selected_image_path')
//     : document.querySelector('#selected_image_path');

//   if(input && window._previewFileUrl) {
//     input.value = window._previewFileUrl; // set hidden input
//   }

//   // Update preview in parent window
//   const preview = window.opener
//     ? window.opener.document.querySelector('#image_preview')
//     : document.querySelector('#image_preview');

//   if(preview) {
//     preview.src = window._previewFileUrl;
//     preview.style.display = 'block';
//   }

//   if(window.closePreview) window.closePreview();

//   if(window.opener){
//     window.close();
//   }
// };

  window.closePreview = function() { document.getElementById('preview-modal').classList.remove('open'); };
  document.getElementById('preview-modal').addEventListener('click', function(e) {
    if (e.target === this) closePreview();
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') { closeFolderModal(); closePreview(); }
  });
})();