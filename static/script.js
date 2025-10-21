// static/script.js

class ChatBot {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendButton');
        this.suggestions = document.querySelectorAll('.suggestion');
        
        // ✅ Session ID simple generado en el frontend
        this.sessionId = 'session-' + Date.now();
        
        this.init();
    }
    
    init() {
        this.displayCurrentTime();
        this.setupEventListeners();
    }
    
    displayCurrentTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('es-MX', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        document.getElementById('currentTime').textContent = timeString;
    }
    
    setupEventListeners() {
        // Enviar mensaje con botón
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enviar mensaje con Enter
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Sugerencias rápidas
        this.suggestions.forEach(suggestion => {
            suggestion.addEventListener('click', () => {
                const question = suggestion.getAttribute('data-question');
                this.userInput.value = question;
                this.sendMessage();
            });
        });
        
        this.userInput.focus();
    }
    
    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;
        
        this.userInput.value = '';
        this.addMessage('user', message);
        this.showTyping();
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    message: message,
                    session_id: this.sessionId  // ✅ Frontend envía session_id
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addMessage('bot', data.bot_response);
            } else {
                this.addMessage('bot', '❌ Error: ' + (data.error || 'Error desconocido'));
            }
            
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('bot', '❌ Error de conexión');
        } finally {
            this.hideTyping();
        }
    }
    
    addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = new Date().toLocaleTimeString('es-MX', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(messageTime);
        this.chatMessages.appendChild(messageDiv);
        
        this.scrollToBottom();
    }
    
    showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
            <div class="message-time">${new Date().toLocaleTimeString('es-MX', { 
                hour: '2-digit', 
                minute: '2-digit' 
            })}</div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTyping() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    new ChatBot();
});