// ────────────────────────────────────────────────────────────────────────────── 
// JARVIS ANALYST - ENHANCED CHAT INTERFACE WITH PSYCHOLOGICAL UX
// ────────────────────────────────────────────────────────────────────────────── 

class JarvisChat {
  constructor() {
    this.api = "http://127.0.0.1:8000/chat";
    this.form = document.getElementById("form");
    this.promptInput = document.getElementById("prompt");
    this.messagesDiv = document.getElementById("messages");
    this.sendButton = document.getElementById("send-btn");
    this.charCount = document.getElementById("char-count");
    this.suggestions = document.getElementById("suggestions");
    this.themeToggle = document.getElementById("theme-toggle");
    
    this.isLoading = false;
    this.messageCounter = 0;
    
    this.init();
  }
  
  init() {
    this.setupEventListeners();
    this.setupTheme();
    this.setupTextareaAutoResize();
    this.showWelcomeMessage();
    this.setupSuggestionChips();
  }
  
  setupEventListeners() {
    // Form submission
    this.form.addEventListener("submit", (e) => this.handleSubmit(e));
    
    // Character counter
    this.promptInput.addEventListener("input", () => this.updateCharCounter());
    
    // Enter key handling (Ctrl+Enter for new line)
    this.promptInput.addEventListener("keydown", (e) => this.handleKeydown(e));
    
    // Theme toggle
    this.themeToggle.addEventListener("click", () => this.toggleTheme());
    
    // Auto-resize textarea
    this.promptInput.addEventListener("input", () => this.autoResizeTextarea());
  }
  
  setupTheme() {
    // Check for saved theme preference or default to system preference
    const savedTheme = localStorage.getItem("jarvis-theme");
    const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    
    if (savedTheme) {
      document.documentElement.setAttribute("data-theme", savedTheme);
    } else if (systemPrefersDark) {
      document.documentElement.setAttribute("data-theme", "dark");
    }
    
    // Listen for system theme changes
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      if (!localStorage.getItem("jarvis-theme")) {
        document.documentElement.setAttribute("data-theme", e.matches ? "dark" : "light");
      }
    });
  }
  
  toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("jarvis-theme", newTheme);
    
    // Add subtle animation feedback
    this.themeToggle.style.transform = "scale(0.9)";
    setTimeout(() => {
      this.themeToggle.style.transform = "scale(1)";
    }, 150);
  }
  
  setupTextareaAutoResize() {
    this.promptInput.style.height = "auto";
    this.promptInput.style.height = this.promptInput.scrollHeight + "px";
  }
  
  autoResizeTextarea() {
    this.promptInput.style.height = "auto";
    this.promptInput.style.height = Math.min(this.promptInput.scrollHeight, 120) + "px";
  }
  
  updateCharCounter() {
    const length = this.promptInput.value.length;
    this.charCount.textContent = length;
    
    // Visual feedback for character limit
    if (length > 900) {
      this.charCount.style.color = "var(--warning-red)";
    } else if (length > 800) {
      this.charCount.style.color = "var(--action-orange)";
    } else {
      this.charCount.style.color = "var(--text-secondary)";
    }
  }
  
  setupSuggestionChips() {
    const chips = this.suggestions.querySelectorAll(".suggestion-chip");
    chips.forEach(chip => {
      chip.addEventListener("click", () => {
        const suggestion = chip.getAttribute("data-suggestion");
        this.promptInput.value = suggestion;
        this.updateCharCounter();
        this.autoResizeTextarea();
        this.promptInput.focus();
        
        // Hide suggestions after use (reduce cognitive load)
        this.hideSuggestions();
      });
    });
  }
  
  hideSuggestions() {
    this.suggestions.style.opacity = "0";
    this.suggestions.style.transform = "translateY(-10px)";
    setTimeout(() => {
      this.suggestions.style.display = "none";
    }, 250);
  }
  
  showSuggestions() {
    this.suggestions.style.display = "flex";
    setTimeout(() => {
      this.suggestions.style.opacity = "1";
      this.suggestions.style.transform = "translateY(0)";
    }, 10);
  }
  
  handleKeydown(e) {
    if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey) {
      e.preventDefault();
      this.handleSubmit(e);
    }
  }
  
  async handleSubmit(e) {
    e.preventDefault();
    
    const text = this.promptInput.value.trim();
    if (!text || this.isLoading) return;
    
    // Hide suggestions after first interaction
    if (this.messageCounter === 0) {
      this.hideSuggestions();
    }
    
    this.isLoading = true;
    this.updateSendButton(true);
    
    // Add user message with animation
    this.addMessage("user", text);
    this.promptInput.value = "";
    this.updateCharCounter();
    this.autoResizeTextarea();
    
    // Add loading spinner with calm teal dots
    const loadingId = this.addLoadingMessage();
    
    try {
      const response = await fetch(this.api, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: text }),
      });
      
      // Remove loading message
      this.removeMessage(loadingId);
      
      if (!response.ok) {
        const errorData = await response.json();
        this.addMessage("error", `${errorData.detail || 'Error del servidor'}`, true);
        return;
      }
      
      const data = await response.json();
      this.addMessage("bot", data.answer);
      
    } catch (error) {
      this.removeMessage(loadingId);
      this.addMessage("error", "Error al conectar con el servidor. Verifica tu conexión.", true);
      console.error("Error:", error);
    } finally {
      this.isLoading = false;
      this.updateSendButton(false);
      this.promptInput.focus();
    }
  }
  
  updateSendButton(loading) {
    this.sendButton.disabled = loading;
    const icon = this.sendButton.querySelector(".send-icon");
    const text = this.sendButton.querySelector(".send-text");
    
    if (loading) {
      icon.setAttribute("data-lucide", "loader-2");
      icon.style.animation = "spin 1s linear infinite";
      text.textContent = "Enviando...";
    } else {
      icon.setAttribute("data-lucide", "send");
      icon.style.animation = "none";
      text.textContent = "Enviar";
    }
    
    // Re-initialize lucide icons
    lucide.createIcons();
  }
  
  addMessage(role, content, isError = false) {
    const messageElement = document.createElement("div");
    const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
    messageElement.id = messageId;
    messageElement.className = isError ? "error" : role;
    
    // Add error icon for error messages
    if (isError) {
      const icon = document.createElement("i");
      icon.setAttribute("data-lucide", "alert-triangle");
      icon.style.width = "16px";
      icon.style.height = "16px";
      icon.style.flexShrink = "0";
      messageElement.appendChild(icon);
    }
    
    // Add message content
    const contentElement = document.createElement("span");
    contentElement.innerHTML = this.formatMessage(content);
    messageElement.appendChild(contentElement);
    
    // Add to messages container
    this.messagesDiv.appendChild(messageElement);
    
    // Initialize lucide icons for error messages
    if (isError) {
      lucide.createIcons();
    }
    
    // Smooth scroll to bottom
    this.scrollToBottom();
    
    this.messageCounter++;
    return messageId;
  }
  
  addLoadingMessage() {
    const template = document.getElementById("loading-template");
    const loadingElement = template.content.cloneNode(true);
    const messageElement = document.createElement("div");
    const messageId = `loading_${Date.now()}`;
    
    messageElement.id = messageId;
    messageElement.className = "bot";
    messageElement.appendChild(loadingElement);
    
    this.messagesDiv.appendChild(messageElement);
    this.scrollToBottom();
    
    return messageId;
  }
  
  removeMessage(messageId) {
    const element = document.getElementById(messageId);
    if (element) {
      // Fade out animation
      element.style.opacity = "0";
      element.style.transform = "translateY(-10px)";
      setTimeout(() => {
        element.remove();
      }, 250);
    }
  }
  
  formatMessage(text) {
    // Convert line breaks to HTML
    let formatted = text.replace(/\n/g, "<br>");
    
    // Simple markdown-like formatting
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    formatted = formatted.replace(/\*(.*?)\*/g, "<em>$1</em>");
    formatted = formatted.replace(/`(.*?)`/g, "<code style='background-color: var(--background-gray); padding: 2px 4px; border-radius: 3px; font-family: monospace;'>$1</code>");
    
    return formatted;
  }
  
  scrollToBottom() {
    // Smooth scroll with easing
    this.messagesDiv.scrollTo({
      top: this.messagesDiv.scrollHeight,
      behavior: "smooth"
    });
  }
  
  showWelcomeMessage() {
    setTimeout(() => {
      this.addMessage("system", "¡Hola! Soy Jarvis Analyst, tu asistente de IA. ¿En qué puedo ayudarte hoy?");
    }, 500);
  }
}

// CSS for spinner animation
const style = document.createElement("style");
style.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  .suggestions {
    transition: opacity 250ms ease, transform 250ms ease;
  }
`;
document.head.appendChild(style);

// Initialize the chat application when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new JarvisChat();
});

// Handle page visibility changes (pause animations when tab is not active)
document.addEventListener("visibilitychange", () => {
  const dots = document.querySelectorAll(".dot");
  dots.forEach(dot => {
    if (document.hidden) {
      dot.style.animationPlayState = "paused";
    } else {
      dot.style.animationPlayState = "running";
    }
  });
});

// Performance optimization: Intersection Observer for message animations
if ("IntersectionObserver" in window) {
  const messageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
  });
  
  // Observe new messages
  const observeNewMessages = () => {
    const messages = document.querySelectorAll(".user, .bot, .system, .error");
    messages.forEach(message => {
      if (!message.dataset.observed) {
        messageObserver.observe(message);
        message.dataset.observed = "true";
      }
    });
  };
  
  // Run initially and on DOM changes
  observeNewMessages();
  
  // Observe for new messages
  const mutationObserver = new MutationObserver(observeNewMessages);
  mutationObserver.observe(document.getElementById("messages"), {
    childList: true
  });
}