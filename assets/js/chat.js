function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

document.addEventListener("DOMContentLoaded", function () {
  const convId = window.CONVERSATION_ID;
  if (!convId) return;
  const messagesEl = document.getElementById("messages");
  const form = document.getElementById("sendForm");

  async function loadMessages() {
    const resp = await fetch(`/mensagens/api/${convId}/messages/`);
    if (!resp.ok) return;
    const data = await resp.json();
    messagesEl.innerHTML = "";
    data.messages.forEach((m) => {
      const d = document.createElement("div");
      d.className =
        "message" + (m.sender__id === window.USER_ID ? " mine" : "");
      d.innerHTML = `<div class="meta">${m.sender__username} — ${m.created_at}</div><div class="content">${m.content}</div>`;
      messagesEl.appendChild(d);
    });
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  // initial load
  loadMessages();

  // poll every 5s for new messages
  setInterval(loadMessages, 5000);

  if (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const fd = new FormData(form);
      const csrftoken = getCookie("csrftoken");
      const resp = await fetch(`/mensagens/api/${convId}/send/`, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
        body: fd,
      });
      if (resp.ok) {
        document.getElementById("msgContent").value = "";
        await loadMessages();
      }
    });
  }
});
