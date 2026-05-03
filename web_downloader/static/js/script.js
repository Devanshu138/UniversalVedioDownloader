document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('download-form');
    const urlInput = document.getElementById('url-input');
    const downloadBtn = document.getElementById('download-btn');
    const btnText = document.querySelector('.btn-text');
    const btnLoader = document.getElementById('btn-loader');
    const terminalContainer = document.getElementById('terminal-container');
    const terminalOutput = document.getElementById('terminal-output');

    let eventSource = null;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const url = urlInput.value.trim();
        if (!url) return;

        // UI State Update
        downloadBtn.disabled = true;
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');
        terminalContainer.classList.remove('hidden');
        terminalOutput.innerHTML = '';
        
        appendLog('Initializing connection...', 'info');

        // Close any existing SSE connection
        if (eventSource) {
            eventSource.close();
        }

        // Start SSE connection
        eventSource = new EventSource(`/api/download?url=${encodeURIComponent(url)}`);

        eventSource.onmessage = function(event) {
            const data = event.data;
            
            if (data === '[DONE]') {
                eventSource.close();
                finishDownload();
                return;
            }

            // Determine line type for styling
            let type = '';
            if (data.includes('[+]') || data.includes('Success')) {
                type = 'success';
            } else if (data.includes('[-]') || data.includes('Error')) {
                type = 'error';
            } else if (data.includes('[*]')) {
                type = 'info';
            }

            appendLog(data, type);
        };

        eventSource.onerror = function(err) {
            console.error('SSE Error:', err);
            appendLog('Connection error occurred. Server might have disconnected.', 'error');
            eventSource.close();
            finishDownload();
        };
    });

    function appendLog(text, type = '') {
        if (!text) return; // Skip empty lines if needed, but we do want spacing sometimes
        
        const line = document.createElement('div');
        line.textContent = text;
        if (type) line.className = type;
        
        terminalOutput.appendChild(line);
        // Auto-scroll to bottom
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }

    function finishDownload() {
        downloadBtn.disabled = false;
        btnText.classList.remove('hidden');
        btnLoader.classList.add('hidden');
    }
});
