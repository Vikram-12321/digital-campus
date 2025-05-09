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
  
  function sharePost(postId) {
    const url = `${location.origin}/posts/${postId}/`;
    if (navigator.share) {
      navigator.share({ title: '{{ object.title }}', url });
    } else {
      navigator.clipboard.writeText(url);
      alert('Link copied to clipboard');
    }
  }