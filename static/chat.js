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
  
  const loadingId = append("bot", "⏳ Procesando...");
  
  try {
    const res = await fetch(api, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        prompt: text
      }),
    });
    
    // Remover mensaje de carga
    removeMessage(loadingId);
    
    if (!res.ok) {
      const errorData = await res.json();
      append("bot", `Error: ${errorData.detail || 'Error del servidor'}`);
      return;
    }
    
    const data = await res.json();
    append("bot", data.answer);
    
  } catch (err) {
    removeMessage(loadingId);
    append("bot", "❌ Error al conectar con el servidor. Verifica tu conexión.");
    console.error('Error:', err);
  }
});

function append(role, text) {
  const p = document.createElement("p");
  const messageId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5);
  p.id = messageId;
  p.className = role;
  
  // Formatear texto con saltos de línea
  p.innerHTML = text.replace(/\n/g, '<br>');
  
  messagesDiv.appendChild(p);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
  
  return messageId;
}

function removeMessage(messageId) {
  const element = document.getElementById(messageId);
  if (element) {
    element.remove();
  }
}

// Agregar funcionalidad de Enter para enviar
promptInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.dispatchEvent(new Event('submit'));
  }
});

window.addEventListener('load', () => {
  append("system", "¡Hola! Soy tu asistente de chat. ¿En qué puedo ayudarte?");
});