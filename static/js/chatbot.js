// Chatbot JavaScript for TaxLyzer application

document.addEventListener('DOMContentLoaded', function() {
    // Set up chatbot toggle button
    const chatButton = document.getElementById('chat-button');
    const chatbotPage = document.getElementById('chatbot-page');
    
    if (chatButton && chatbotPage) {
        chatButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Hide home and all content pages
            document.getElementById('home-page').classList.add('d-none');
            document.getElementById('magic-section').classList.add('d-none');
            
            document.querySelectorAll('.content-page').forEach(page => {
                page.classList.add('d-none');
            });
            
            // Show chatbot page
            chatbotPage.classList.remove('d-none');
            
            // Update active nav link
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            this.classList.add('active');
            
            // Scroll to the bottom of the chat
            scrollToBottom();
        });
    }
    
    // Set up send message button
    const sendButton = document.getElementById('send-message');
    const messageInput = document.getElementById('message-input');
    
    if (sendButton && messageInput) {
        // Send on button click
        sendButton.addEventListener('click', sendMessage);
        
        // Send on Enter key
        messageInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});

// Send user message to the server
function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    if (message === '') return;
    
    // Add user message to the UI
    addMessageToUI(message, 'user');
    
    // Clear input
    messageInput.value = '';
    
    // Show typing indicator
    addTypingIndicator();
    
    // Call chatbot API
    fetch('/api/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        // Remove typing indicator
        removeTypingIndicator();
        
        // Add bot response to the UI
        if (data.error) {
            addMessageToUI('Sorry, I encountered an error: ' + data.error, 'bot');
        } else {
            addMessageToUI(data.response, 'bot');
        }
    })
    .catch(error => {
        console.error('Error calling chatbot API:', error);
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Show error message
        addMessageToUI('Sorry, I encountered an error. Please try again later.', 'bot');
    });
}

// Add a message to the chat UI
function addMessageToUI(message, type) {
    const chatMessages = document.getElementById('chat-messages');
    
    if (!chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}-message d-flex mb-3 ${type === 'user' ? 'justify-content-end' : ''}`;
    
    // Format message text, handle line breaks and links
    const formattedMessage = message
        .replace(/\n/g, '<br>')
        .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    
    messageElement.innerHTML = `
        <div class="message-content p-3 rounded ${type === 'user' ? 'text-white' : ''}">
            <p>${formattedMessage}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    
    // Scroll to the bottom
    scrollToBottom();
}

// Add typing indicator to the chat
function addTypingIndicator() {
    const chatMessages = document.getElementById('chat-messages');
    
    if (!chatMessages) return;
    
    // Check if typing indicator already exists
    if (document.querySelector('.typing-indicator')) return;
    
    const typingElement = document.createElement('div');
    typingElement.className = 'message bot-message d-flex mb-3 typing-indicator';
    
    typingElement.innerHTML = `
        <div class="message-content p-3 rounded">
            <p>Typing<span class="dot-one">.</span><span class="dot-two">.</span><span class="dot-three">.</span></p>
        </div>
    `;
    
    chatMessages.appendChild(typingElement);
    
    // Scroll to the bottom
    scrollToBottom();
}

// Remove typing indicator from the chat
function removeTypingIndicator() {
    const typingIndicator = document.querySelector('.typing-indicator');
    
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Scroll to the bottom of the chat messages
function scrollToBottom() {
    const chatMessages = document.getElementById('chat-messages');
    
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}
