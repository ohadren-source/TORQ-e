// claude-stream.js — Universal Claude SSE streaming logic for TORQ-e
// Include this file in any card. Call initClaudeStream(config) to wire up.
//
// Usage:
//   <script src="/static/claude-stream.js"></script>
//   <script>
//     initClaudeStream({ userType: 'DataAnalyst', cardNumber: 5 });
//   </script>

function initClaudeStream(config) {
    const userType   = config.userType   || 'Member';
    const cardNumber = config.cardNumber || 1;

    const inputText   = document.getElementById('inputText');
    const sendBtn     = document.getElementById('sendBtn');
    const messagesDiv = document.getElementById('messages');

    if (!inputText || !sendBtn || !messagesDiv) {
        console.error('claude-stream.js: missing inputText, sendBtn, or messages element.');
        return;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.appendChild(document.createTextNode(text));
        return div.innerHTML;
    }

    // Auto-resize textarea
    inputText.addEventListener('input', () => {
        inputText.style.height = 'auto';
        inputText.style.height = inputText.scrollHeight + 'px';
    });

    // Enter to send
    inputText.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Button click
    sendBtn.addEventListener('click', sendMessage);

    async function callClaudeAPI(message, bubble) {
        try {
            const response = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    userType: userType,
                    cardNumber: cardNumber,
                    sessionId: sessionStorage.getItem('sessionId') || 'session-' + Date.now()
                })
            });

            if (!response.ok) throw new Error('API error: ' + response.status);

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            bubble.textContent = '';

            let fullText = '';
            let lineBuffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                const combined = lineBuffer + chunk;
                const lines = combined.split('\n');
                lineBuffer = lines.pop();
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.text) {
                                fullText += data.text;
                                bubble.textContent = fullText;
                                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                            }
                        } catch(e) {}
                    }
                }
            }
            if (lineBuffer.startsWith('data: ')) {
                try {
                    const data = JSON.parse(lineBuffer.slice(6));
                    if (data.text) fullText += data.text;
                } catch(e) {}
            }

            // Render markdown if markdown-it + DOMPurify are loaded
            if (window.markdownit && window.DOMPurify) {
                const md = window.markdownit({ html: false, linkify: true, typographer: true });
                bubble.innerHTML = DOMPurify.sanitize(md.render(fullText));
            } else {
                bubble.textContent = fullText;
            }
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

        } catch (error) {
            bubble.textContent = 'Error: ' + error.message;
        }
    }

    async function sendMessage() {
        const message = inputText.value.trim();
        if (!message) return;

        const userDiv = document.createElement('div');
        userDiv.className = 'message user';
        userDiv.innerHTML = '<div class="message-bubble">' + escapeHtml(message) + '</div>';
        messagesDiv.appendChild(userDiv);

        inputText.value = '';
        inputText.style.height = 'auto';
        sendBtn.disabled = true;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

        const assistantDiv = document.createElement('div');
        assistantDiv.className = 'message assistant';
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = 'Analyzing...';
        assistantDiv.appendChild(bubble);
        messagesDiv.appendChild(assistantDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

        await callClaudeAPI(message, bubble);

        sendBtn.disabled = false;
        inputText.focus();
    }

    // Expose askSuggested globally for onclick handlers in HTML
    window.askSuggested = function(text) {
        inputText.value = text;
        inputText.focus();
        inputText.style.height = 'auto';
        inputText.style.height = inputText.scrollHeight + 'px';
    };
}
