$(function () {
    $('[data-toggle="tooltip"]').tooltip();
  });

function initCollapsibles() {
    document.querySelectorAll('.collapsible-content').forEach(box => {
      const toggle = box.parentElement.querySelector('.expand-toggle');
      if (!toggle) return;
      // measure full height
      const fullHeight = box.scrollHeight;
      const threshold = 300; // must match your CSS max-height
      if (fullHeight > threshold) {
        // content is taller than 300px → make it collapsible
        box.classList.add('collapsed');
        toggle.style.display = 'block';
        const icon = toggle.querySelector('i');
        icon.className = 'bi bi-chevron-down';
        if (!toggle.dataset.bound) {
          toggle.dataset.bound = 'true';
          toggle.addEventListener('click', () => {
            const nowCollapsed = box.classList.toggle('collapsed');
            icon.className = nowCollapsed ? 'bi bi-chevron-down' : 'bi bi-chevron-up';
          });
        }
      } else {
        // content fits within 300px → no arrow
        toggle.style.display = 'none';
        box.classList.remove('collapsed');
      }
    });
  }
  window.addEventListener('load', initCollapsibles);

  document.addEventListener('DOMContentLoaded', () => {
    const videoInput = document.querySelector('input[type=file][name=video]');
    if (!videoInput) return;
    videoInput.addEventListener('change', () => {
      const file = videoInput.files[0];
      if (file && file.size > 50 * 1024 * 1024) {
        alert('That video is over 50MB – please choose a smaller file.');
        videoInput.value = ''; // clear it
      }
    });
  });

  $(function () {
    $('#id_search_input').autocomplete({
      source: function (request, response) {
        $.getJSON(autocompleteURL, { term: request.term }, function (data) {
          const grouped = {};

          data.forEach(item => {
            const group = `${item.type}s`;
            if (!grouped[group]) grouped[group] = [];
            grouped[group].push(item);
          });

          const flattened = [];
          for (const group in grouped) {
            flattened.push({ label: group, isGroupHeader: true });
            grouped[group].forEach(i => flattened.push(i));
          }

          response(flattened);
        });
      },
      minLength: 2,
      appendTo: '#dc-search-group',
      position: {
        my: 'left top',
        at: 'left bottom',
        of: '#dc-search-group',
        collision: 'flipfit'
      },
      select: function (event, ui) {
        if (ui.item.isGroupHeader) {
          event.preventDefault();
          return false;
        }
        window.location.href = ui.item.url;
      }
    }).autocomplete("instance")._renderItem = function (ul, item) {
      if (item.isGroupHeader) {
        return $("<li class='ui-search-group'></li>").text(item.label).appendTo(ul);
      }

      return $("<li>").append(`
        <div class="ui-search-result">
          <img src="${item.image ||''}" alt="" class="ui-search-avatar">
          <div class="ui-search-text">
            <div class="ui-search-title">${item.label}</div>
            <div class="ui-search-sub">${item.subtitle || ''}</div>
            <div class="ui-search-snippet">${item.snippet|| ''}</div>
          </div>
        </div>
      `).appendTo(ul);
    };
  });