// CSRF helper for POST requests (works in static file, no template vars needed)
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

function resolveCsrfToken() {
  let t = getCookie('csrftoken');
  if (!t) {
    const input = document.querySelector('#dc-csrf-init input[name="csrfmiddlewaretoken"], input[name="csrfmiddlewaretoken"]');
    if (input) t = input.value;
  }
  if (t && t.toUpperCase() === 'NOTPROVIDED') t = '';
  return t;
}

function toggleLike(postId) {
  fetch(`/posts/${postId}/like/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': resolveCsrfToken(),
      'X-Requested-With': 'XMLHttpRequest'
    },
    credentials: 'same-origin'
  })
    .then(r => r.ok ? r.json() : Promise.reject(r))
    .then(data => {
      const btn = document.getElementById(`like-btn-${postId}`);
      if (btn) btn.classList.toggle('active', data.liked);
    })
    .catch(() => console.warn('Like request failed'));
}

function toggleShareMenu(postId) {
  // Collapse all open menus
  document.querySelectorAll('.share-menu.collapse.show').forEach(el => {
    bootstrap.Collapse.getInstance(el)?.hide();
  });

  const menu = document.getElementById(`share-menu-${postId}`);
  new bootstrap.Collapse(menu, { toggle: true });

  const url = `${location.origin}/post/${postId}/`;
  const titleEl = document.getElementById(`post-title-${postId}`);
  const title = titleEl ? titleEl.textContent.trim() : '';

  const twitter = document.getElementById(`twitter-share-${postId}`);
  const whatsapp = document.getElementById(`whatsapp-share-${postId}`);
  if (twitter) twitter.href = `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`;
  if (whatsapp) whatsapp.href = `https://wa.me/?text=${encodeURIComponent(title + ' ' + url)}`;
}

function closeShareMenu(postId) {
  const menu = document.getElementById(`share-menu-${postId}`);
  bootstrap.Collapse.getInstance(menu)?.hide();
}

function copyLink(postId) {
  const url = `${location.origin}/posts/${postId}/`;
  navigator.clipboard.writeText(url).then(() => {
    alert('Link copied to clipboard!');
  });
}

function copyInstagramLink(postId) {
  const url = `${location.origin}/posts/${postId}/`;
  navigator.clipboard.writeText(url).then(() => {
    alert("Instagram doesn't support web sharing. Link copied!");
  });
}
