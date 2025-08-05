class JarvisChat {
    constructor() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.form = document.getElementById('chatForm');
        this.promptInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendBtn');
        this.charCount = document.getElementById('charCount');
        this.suggestionsContainer = document.getElementById('suggestionChips');
        this.themeToggle = document.getElementById('themeToggle');
        this.mobileMenuBtn = document.getElementById('mobileMenuBtn');

        this.isLoading = false;
        this.messageHistory = [];

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupTheme();
        this.addWelcomeMessage();
        this.autoResizeTextarea();
        this.setupScrollEffects();
    }

    setupEventListeners() {
        // Form submission
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        // Input character counting and auto-resize
        if (this.promptInput) {
            this.promptInput.addEventListener('input', () => {
                this.updateCharCount();
                this.autoResizeTextarea();
                this.toggleSendButton();
            });

            // Enter key handling (submit on Enter, new line on Shift+Enter)
            this.promptInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (!this.isLoading && this.promptInput.value.trim()) {
                        this.handleSubmit(e);
                    }
                }
            });
        }

        // Theme toggle
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Mobile menu (placeholder for future implementation)
        if (this.mobileMenuBtn) {
            this.mobileMenuBtn.addEventListener('click', () => this.toggleMobileMenu());
        }

        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    setupTheme() {
        // Theme is already set by the script in HTML head
        // Just handle the toggle functionality
        const updateThemeIcon = () => {
            const isDark = document.documentElement.classList.contains('dark');
            const sunIcon = this.themeToggle?.querySelector('.sun-icon');
            const moonIcon = this.themeToggle?.querySelector('.moon-icon');

            if (sunIcon && moonIcon) {
                if (isDark) {
                    sunIcon.style.opacity = '0';
                    sunIcon.style.transform = 'rotate(180deg)';
                    moonIcon.style.opacity = '1';
                    moonIcon.style.transform = 'rotate(0deg)';
                } else {
                    sunIcon.style.opacity = '1';
                    sunIcon.style.transform = 'rotate(0deg)';
                    moonIcon.style.opacity = '0';
                    moonIcon.style.transform = 'rotate(-180deg)';
                }
            }
        };

        updateThemeIcon();

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                document.documentElement.classList.toggle('dark', e.matches);
                updateThemeIcon();
            }
        });
    }

    toggleTheme() {
        const isDark = document.documentElement.classList.contains('dark');
        const newTheme = isDark ? 'light' : 'dark';

        document.documentElement.classList.toggle('dark', !isDark);
        localStorage.setItem('theme', newTheme);

        // Update icon with animation
        const sunIcon = this.themeToggle?.querySelector('.sun-icon');
        const moonIcon = this.themeToggle?.querySelector('.moon-icon');

        if (sunIcon && moonIcon) {
            if (!isDark) { // switching to dark
                sunIcon.style.opacity = '0';
                sunIcon.style.transform = 'rotate(180deg)';
                moonIcon.style.opacity = '1';
                moonIcon.style.transform = 'rotate(0deg)';
            } else { // switching to light
                sunIcon.style.opacity = '1';
                sunIcon.style.transform = 'rotate(0deg)';
                moonIcon.style.opacity = '0';
                moonIcon.style.transform = 'rotate(-180deg)';
            }
        }

        // Add subtle animation feedback
        if (this.themeToggle) {
            this.themeToggle.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.themeToggle.style.transform = 'scale(1)';
            }, 150);
        }
    }

    toggleMobileMenu() {
        // Placeholder for mobile menu functionality
        console.log('Mobile menu toggle - to be implemented');
    }

    setupScrollEffects() {
        // Header shrink effect on scroll
        let lastScrollY = window.scrollY;
        let ticking = false;

        // Cross-browser requestAnimationFrame fallback
        const requestAnimFrame = window.requestAnimationFrame ||
            window.webkitRequestAnimationFrame ||
            window.mozRequestAnimationFrame ||
            window.oRequestAnimationFrame ||
            window.msRequestAnimationFrame ||
            function (callback) {
                return window.setTimeout(callback, 1000 / 60);
            };

        const updateHeader = () => {
            const header = document.querySelector('.header');
            const headerContent = document.querySelector('.header-content');
            const body = document.body;

            if (header && headerContent && body) {
                if (window.scrollY > 50) {
                    header.classList.add('scrolled');
                    body.classList.add('header-scrolled');
                    headerContent.style.height = '3.5rem';
                } else {
                    header.classList.remove('scrolled');
                    body.classList.remove('header-scrolled');
                    headerContent.style.height = '4rem';
                }
            }
            ticking = false;
        };

        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimFrame(updateHeader);
                ticking = true;
            }
            lastScrollY = window.scrollY;
        });
    }

    addWelcomeMessage() {
        if (!this.messagesContainer) return;

        const welcomeMessage = {
            role: 'assistant',
            content: '¡Hola! Soy Jarvis, tu asistente de análisis conversacional. Puedo ayudarte a analizar datos, responder preguntas complejas y generar insights valiosos. ¿En qué puedo ayudarte hoy?'
        };

        this.addMessage(welcomeMessage);
    }

    async handleSubmit(e) {
        e.preventDefault();

        if (!this.promptInput || !this.messagesContainer) return;

        const message = this.promptInput.value.trim();
        if (!message || this.isLoading) return;

        // Hide suggestion chips after first message
        if (this.suggestionsContainer && this.messageHistory.length === 1) {
            this.suggestionsContainer.style.display = 'none';
        }

        // Add user message
        this.addMessage({ role: 'user', content: message });

        // Clear input and reset
        this.promptInput.value = '';
        this.updateCharCount();
        this.autoResizeTextarea();
        this.toggleSendButton();

        // Show loading state
        this.setLoading(true);

        try {
            const response = await this.sendToAPI(message);
            this.addMessage({ role: 'assistant', content: response });
        } catch (error) {
            console.error('Error:', error);
            this.addMessage({
                role: 'error',
                content: 'Lo siento, ha ocurrido un error. Por favor, inténtalo de nuevo.'
            });
        } finally {
            this.setLoading(false);
        }
    }

    async sendToAPI(message) {
        const response = await fetch('/api/chat/completion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                messages: [{ role: 'user', content: message }],
                temperature: 0.7,
                max_tokens: 1000,
                stream: false
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.answer || 'No se pudo obtener una respuesta.';
    }

    addMessage(message) {
        if (!this.messagesContainer) return;

        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.role}`;

        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        contentElement.innerHTML = this.formatMessage(message.content);

        messageElement.appendChild(contentElement);
        this.messagesContainer.appendChild(messageElement);

        // Initialize Lucide icons for new content
        this.initializeLucideIcons();

        // Smooth scroll to bottom
        this.scrollToBottom();

        // Store in history
        this.messageHistory.push(message);
    }

    formatMessage(content) {
        // Basic markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code style="background: rgba(255,255,255,0.1); padding: 0.125rem 0.25rem; border-radius: 0.25rem;">$1</code>')
            .replace(/\n/g, '<br>');
    }

    setLoading(loading) {
        this.isLoading = loading;

        if (loading) {
            // Show loading spinner
            const loadingSpinner = document.getElementById('loadingSpinner');
            if (loadingSpinner) {
                loadingSpinner.style.display = 'block';
            }
        } else {
            // Hide loading spinner
            const loadingSpinner = document.getElementById('loadingSpinner');
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            }
        }

        this.toggleSendButton();
    }

    updateCharCount() {
        if (!this.promptInput || !this.charCount) return;

        const count = this.promptInput.value.length;
        this.charCount.textContent = `${count}/500`;

        // Color coding for character limit
        if (count > 450) {
            this.charCount.style.color = '#EF4444'; // red
        } else if (count > 400) {
            this.charCount.style.color = '#F59E0B'; // orange
        } else {
            this.charCount.style.color = 'rgba(255, 255, 255, 0.5)';
        }
    }

    autoResizeTextarea() {
        if (!this.promptInput) return;

        this.promptInput.style.height = 'auto';
        const newHeight = Math.min(this.promptInput.scrollHeight, 96); // max 6rem
        this.promptInput.style.height = newHeight + 'px';
    }

    toggleSendButton() {
        if (!this.promptInput || !this.sendButton) return;

        const hasContent = this.promptInput.value.trim().length > 0;
        this.sendButton.disabled = !hasContent || this.isLoading;

        if (this.isLoading) {
            this.sendButton.innerHTML = `
                <div class="spinner" style="scale: 0.7;">
                    <div class="dot dot-1"></div>
                    <div class="dot dot-2"></div>
                    <div class="dot dot-3"></div>
                </div>
            `;
        } else {
            this.sendButton.innerHTML = '<i data-lucide="send"></i>';

            // Re-initialize Lucide icons
            this.initializeLucideIcons();
        }
    }

    scrollToBottom() {
        if (!this.messagesContainer) return;

        // Use Intersection Observer for performance
        if ('IntersectionObserver' in window) {
            const lastMessage = this.messagesContainer.lastElementChild;
            if (lastMessage) {
                lastMessage.scrollIntoView({
                    behavior: 'smooth',
                    block: 'end'
                });
            }
        } else {
            // Fallback for older browsers
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }

    // Centralized method for Lucide icon initialization
    initializeLucideIcons() {
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    // Public method to send message programmatically
    sendMessage(message) {
        if (!this.promptInput) return;

        this.promptInput.value = message;
        this.updateCharCount();
        this.autoResizeTextarea();
        this.toggleSendButton();
        this.handleSubmit(new Event('submit'));
    }
}

// Global function for suggestion chips
function sendSuggestion(text) {
    if (window.jarvisChat) {
        window.jarvisChat.sendMessage(text);
    }
}

// Global function for smooth scrolling
function scrollToChat() {
    const chatSection = document.getElementById('chat');
    if (chatSection) {
        chatSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.jarvisChat = new JarvisChat();

    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Add loading animation to page elements
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe feature cards and other elements
    document.querySelectorAll('.feature-card, .stat, .hero-badge').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JarvisChat;
}