async function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    const sendButton = document.getElementById('send-button');
    if (userInput.trim() === "") return; // Do nothing if input is empty
    
    displayMessage(userInput, "user");
    document.getElementById('user-input').value = ""; // Clear the input field

    sendButton.disabled = true;
    answer = displayMessage("...", "bot");
    
    // Call GPT-4 mini API
    const botResponse = await getBotResponse(userInput);
    message = formatMessage(botResponse);
    answer.innerHTML = message;

    // Trigger MathJax to process any LaTeX math expressions in the message
    MathJax.Hub.Queue(["Typeset", MathJax.Hub]);

    sendButton.disabled = false;
}

async function getBotResponse(userInput) {
    const response = await fetch("/bot-response", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: userInput })
    });

    if (!response.ok) {
        return "Desculpe, houve um erro no processamento da resposta.";
    }

    const data = await response.json();
    return data.message;
}

function formatMessage(message) {
    // Convert bold
    message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Convert italic
    message = message.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Convert inline code
    message = message.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Convert headings
    message = message.replace(/^(#+)\s*(.+)$/gm, (match, hashes, headingText) => {
        const level = hashes.length;
        return `<h${level}>${headingText}</h${level}>`;
    });

    // Convert links
    message = message.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>');

    // Convert newlines
    message = message.replace(/\n/g, '<br>');

    return message;
}

function displayMessage(message, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', sender);
    
    const messageContent = document.createElement('p');
    messageContent.innerHTML = message;

    messageElement.appendChild(messageContent);
    chatBox.appendChild(messageElement);
    
    // Scroll to the latest message
    chatBox.scrollTop = chatBox.scrollHeight;

    return messageContent;
}

// Enable the user to send message by pressing Enter
document.getElementById('user-input').addEventListener('keydown', function (e) {
    const sendButton = document.getElementById('send-button');
    if (e.key === 'Enter' && !sendButton.disabled) {
        sendMessage();
    }
});