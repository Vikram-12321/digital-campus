// chat.js
(function () {
  const { roomName, userName, uploadUrl, csrfToken } = window.CHAT;
  const socket = new WebSocket(`ws://${location.host}/ws/chat/${roomName}/`);

  /* ---------- DOM ---------- */
  const $messages = $('#messages-container');
  const $msgInput = $('#msg-input');
  const $typing = $('#typing-indicator');
  const $typingUser = $('#typing-user');
  const $fileInput = $('#file-input');

  /* ---------- Helpers ---------- */
  const scrollBottom = () => $messages.prop('scrollTop', $messages.prop('scrollHeight'));

  const renderMessage = data => {
    const { username, message, profile_pic_url, timestamp } = data;

    const $media = $(`
      <div class="media mb-3">
         <img src="${profile_pic_url || 'https://via.placeholder.com/40'}"
              class="mr-3 rounded-circle" width="40" height="40">
         <div class="media-body">
             <h6 class="mt-0 mb-1">${username}
               <small class="text-muted">${timestamp}</small>
             </h6>
             <p class="mb-1">${message || ''}</p>
         </div>
      </div>`);
    $messages.append($media);
    scrollBottom();
  };

  /* ---------- WebSocket events ---------- */
  socket.onmessage = e => {
    const data = JSON.parse(e.data);
    if (data.type === 'typing') {
      if (data.user !== userName) {
        $typingUser.text(data.user);
        $typing.show();
        clearTimeout($typing.data('timeout'));
        $typing.data('timeout', setTimeout(() => $typing.hide(), 1500));
      }
    } else {
      $typing.hide();
      renderMessage(data);
    }
  };

  socket.onclose = () => console.warn('Socket closed');

  /* ---------- Send text ---------- */
  $('#composer').on('submit', e => {
    e.preventDefault();
    const msg = $msgInput.val().trim();
    if (msg) {
      socket.send(JSON.stringify({ message: msg }));
      $msgInput.val('');
    }
  });

  /* ---------- Typing indicator ---------- */
  let typingTimeout;
  $msgInput.on('input', () => {
    clearTimeout(typingTimeout);
    socket.send(JSON.stringify({ type: 'typing' }));
    typingTimeout = setTimeout(() => {}, 1000);
  });

  /* ---------- File upload ---------- */
  $fileInput.on('change', () => {
    const file = $fileInput[0].files[0];
    if (!file) return;

    const form = new FormData();
    form.append('file', file);
    form.append('room_name', roomName);

    fetch(uploadUrl, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken },
      body: form,
    })
    .then(r => r.json())
    .then(() => {
        socket.send(JSON.stringify({ message: `${userName} sent a file.` }));
    })
    .catch(console.error);
  });

  /* ---------- Auto-scroll on load ---------- */
  $(document).ready(scrollBottom);
})();
