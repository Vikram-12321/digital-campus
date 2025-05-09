let page     = 2;      // first Ajax page
let loading  = false;
let finished = false;  // flips to true when server sends an empty slice

function currentFilter () {
  const p = new URLSearchParams(window.location.search);
  return p.get('filter_by') || 'all';
}

async function loadNext () {
  if (finished || loading) return;
  loading = true;
  document.getElementById('loading').style.display = 'block';

  try {
    const res = await fetch(`?page=${page}&filter_by=${currentFilter()}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    const data = await res.json();       // blank JSON if 404 intercepted
    if (data.posts_html && data.posts_html.trim()) {
      document
        .getElementById('post-container')
        .insertAdjacentHTML('beforeend', data.posts_html);
      page++;
      loading = false;
      document.getElementById('loading').style.display = 'none';
    } else {
      finished = true;
      document.getElementById('loading').innerText = 'No more items';
    }
  } catch (e) {
    console.error('Infinite scroll error:', e);
    finished = true;
    document.getElementById('loading').innerText = 'Couldn’t load more';
  }
}

window.addEventListener('scroll', () => {
  if (
    !finished && !loading &&
    window.innerHeight + window.scrollY >= document.body.offsetHeight - 100
  ) {
    loadNext();
  }
});