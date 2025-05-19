function toggleLike(postId) {
    fetch(`/posts/${postId}/like/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': '{{ csrf_token }}' }
    })
    .then(r => r.json())
    .then(data => {
      const btn = document.getElementById(`like-btn-${postId}`);
      if (btn) btn.classList.toggle('active', data.liked);
    });
  }
  
function toggleShareMenu(postId) {
  // Collapse all open menus
  document.querySelectorAll('.share-menu.collapse.show').forEach(el => {
    bootstrap.Collapse.getInstance(el)?.hide();
  });

  const menu = document.getElementById(`share-menu-${postId}`);
  const collapse = new bootstrap.Collapse(menu, { toggle: true });

  const url = `${location.origin}/posts/${postId}/`;
  const title = '{{ object.title|escapejs }}';

  document.getElementById(`twitter-share-${postId}`).href =
    `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`;

  document.getElementById(`whatsapp-share-${postId}`).href =
    `https://wa.me/?text=${encodeURIComponent(title + ' ' + url)}`;
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
    alert('Instagram doesn\'t support web sharing. Link copied!');
  });
}

console.log("Hello from post_detail.js!");