function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    const chatlog = document.getElementById('chatlog');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const microphoneIcon = document.getElementById('microphone-icon');
    let isListening = false;
    let recorder;  // Variable to hold the MediaRecorder instance

    // Scroll to the bottom of the chat log
    chatlog.scrollTop = chatlog.scrollHeight;

    // Send the user message to the server when the user submits the form
    chatForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Get user input
        const userMessage = userInput.value;

        // Clear the input field
        userInput.value = '';

        // Add the user message to the chat log
        chatlog.innerHTML += '<div class="user-message">' + userMessage + '</div>';

        // Send the user message to the server and get the response
        fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            },
            body: 'user_input=' + encodeURIComponent(userMessage)
        })
        .then(response => response.json())
        .then(data => {
            // Add the bot response to the chat log
            chatlog.innerHTML += '<div class="bot-message">' + data.bot_response + '</div>'
            // Scroll to the bottom of the chat log
            chatlog.scrollTop = chatlog.scrollHeight;
        })
        .catch(error => console.error('Error:', error));
    });

    
    microphoneIcon.addEventListener('click', function() {
        if (!isListening) {
            // Start recording
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(str => {
                    stream = str;
                    recorder = RecordRTC(stream, { type: 'audio' });
                    recorder.startRecording();

                    // Change the microphone icon to green
                    microphoneIcon.style.backgroundColor = 'green';

                    isListening = true;
                });
        } else {
            // Stop recording
            if (recorder) {
                recorder.stopRecording(() => {
                    let blob = recorder.getBlob();
                    const formData = new FormData();
                    formData.append('audio_data', blob, 'audio.webm');
                    fetch('/transcribe/', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken') 
                        }
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log(data);
                        // Update the input box with the transcribed text
                        userInput.value = data.text;
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
    
                    // Stop the stream
                    stream.getAudioTracks().forEach(track => track.stop());

                    // Change the microphone icon back to black
                    microphoneIcon.style.backgroundColor = '';
    
                    // Set isListening to false
                    isListening = false;
                });
            }
        }
    });
});


