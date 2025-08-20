// ---------- Upload ----------
const uploadForm = document.getElementById("uploadForm");
if (uploadForm) {
  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const status = document.getElementById("uploadStatus");
    const formData = new FormData(uploadForm);
    try {
      status.textContent = "Uploading…";
      const res = await fetch("/upload", { method: "POST", body: formData });
      const data = await res.json();
      status.textContent = res.ok ? data.message : data.error;
    } catch (err) {
      status.textContent = "Network error";
    }
  });
}

// ---------- Chat ----------
const chatForm = document.getElementById("chatForm");
if (chatForm) {
  const chatWindow = document.getElementById("chatWindow");
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = document.getElementById("userInput");
    const q = input.value.trim();
    if (!q) return;
    renderMsg("user", q);
    input.value = "";

    try {
      const body = new URLSearchParams({ question: q });
      const res = await fetch("/query", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body
      });
      const data = await res.json();
      if (res.ok) renderMsg("bot", data.answer);
      else renderMsg("bot", data.error || "Error");
    } catch {
      renderMsg("bot", "Network error");
    }
  });

  function renderMsg(role, text) {
    const div = document.createElement("div");
    div.className = role === "bot" ? "botMsg" : "userMsg";
    div.textContent = (role === "bot" ? "🤖 " : "🧑 ") + text;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }
}
