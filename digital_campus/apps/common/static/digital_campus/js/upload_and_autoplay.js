// upload_and_autoplay.js


document.addEventListener('DOMContentLoaded', () => {
  // ——— 1) DRAG & DROP ZONE ———
  const zone       = document.querySelector('.upload-zone');
  const imgInput   = document.getElementById('id_image');
  const videoInput = document.getElementById('id_video');
  const picker     = document.getElementById('zone-file-input');

  if (zone && imgInput && videoInput && picker) {
    ['dragenter','dragover'].forEach(evt =>
      zone.addEventListener(evt, e => {
        e.preventDefault();
        zone.classList.add('dragover');
      })
    );
    ['dragleave','drop'].forEach(evt =>
      zone.addEventListener(evt, e => {
        e.preventDefault();
        zone.classList.remove('dragover');
      })
    );
    zone.addEventListener('drop', e => {
      const file = e.dataTransfer.files[0];
      handleFile(file);
    });
    zone.addEventListener('click', () => picker.click());
    picker.addEventListener('change', () => {
      const file = picker.files[0];
      handleFile(file);
    });
  }

  function handleFiles(files) {
    const inputs = Array.from(document.querySelectorAll('.attachment-input input[type=file]'));
    files = Array.from(files);
    files.forEach((file, i) => {
      if (i >= inputs.length) return; // ignore extras
      const dt = new DataTransfer();
      dt.items.add(file);
      inputs[i].files = dt.files;
      // show preview in zone
      if (file.type.startsWith('image/')) {
        zone.innerHTML += `<img src="${URL.createObjectURL(file)}">`;
      } else {
        zone.innerHTML += `<video src="${URL.createObjectURL(file)}" muted playsinline></video>`;
      }
    });
  }
  

  // ——— 2) AUTOPLAY VIDEOS IN VIEWPORT ———
  const videos = document.querySelectorAll('video[controls]');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const vid = entry.target;
      if (entry.isIntersecting) {
        vid.play().catch(err => console.warn('Autoplay prevented:', err));
      } else {
        vid.pause();
      }
    });
  }, {
    threshold: 0.5  // play when 50% visible
  });

  videos.forEach(vid => {
    observer.observe(vid);
  });
});
