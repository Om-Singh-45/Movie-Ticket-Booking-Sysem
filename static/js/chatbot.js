function openChatbot() {
    document.getElementById('chatbot-container').style.display = 'block';
}

document.getElementById('chatbox-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        const message = this.value;
        const chatboxBody = document.getElementById('chatbox-body');
        
        chatboxBody.innerHTML += `<div class="user-message">${message}</div>`;
        this.value = '';

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        })
        .then(response => response.json())
        .then(data => {
            chatboxBody.innerHTML += `<div class="bot-response">${data.response}</div>`;
        })
        .catch(error => console.error('Error:', error));
    }
});
