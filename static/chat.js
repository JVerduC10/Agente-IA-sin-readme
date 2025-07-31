const api = "http://127.0.0.1:8000/chat";
const form = document.getElementById("form");
const promptInput = document.getElementById("prompt");
const messagesDiv = document.getElementById("messages");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = promptInput.value.trim();
  if (!text) return;
  append("user", text);
  promptInput.value = "";
  try {
    const res = await fetch(api, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({prompt: text}),
    });
    const data = await res.json();
    append("bot", data.answer);
  } catch (err) {
    append("bot", "Error al conectar con el servidor");
  }
});

function append(role, text) {
  const p = document.createElement("p");
  p.className = role;
  p.textContent = text;
  messagesDiv.appendChild(p);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}