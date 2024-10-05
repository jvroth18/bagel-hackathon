from flask import Flask, render_template, request, send_file
import requests
import io
import os
import logging

app = Flask(__name__)

# Replace with your Cloud Run API endpoint URL
ENDPOINT = "enter-your-server/chat"

@app.route('/')
def index():
    return ''' 
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Audio Chatbot</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Architects+Daughter&display=swap');

            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                text-align: center;
                padding: 20px;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #fff;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .logo {
                display: block;
                margin: 0 auto 10px;
                height: 50px;
            }
            h1 {
                font-size: 28px;
                margin-bottom: 20px;
            }
            #recordButton {
                width: 200px;
                height: 60px;
                font-size: 18px;
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                margin-bottom: 20px;
            }
            #recordButton:active {
                background-color: #E64A19;
            }
            .question-buttons {
                display: flex;
                justify-content: center;
                gap: 10px;
                margin-bottom: 20px;
            }
            .question-buttons button {
                background-color: transparent;
                color: black;
                padding: 10px 15px;
                border: 1px solid black;
                border-radius: 20px;
                cursor: pointer;
            }
            .question-buttons button:hover {
                background-color: #f0f0f0;
            }
            audio {
                margin-top: 20px;
            }
            .footer {
                margin-top: 30px;
                text-align: center;
                position: relative;
            }
            .footer-content {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 10px;
            }
            .footer img {
                height: 50px;
            }
            .footer p {
                font-size: 20px;
                font-weight: bold;
                color: #333;
                margin: 0;
            }
            .handwritten {
                font-family: 'Architects Daughter', cursive;
                font-size: 18px;
                margin-top: 5px;
                transform: rotate(-3deg);
                display: inline-block;
            }
            .split-text {
                margin-top: 5px;
            }
            .heading {
                font-size: 18px;
                margin-bottom: 10px;
                color: #333;
                font-style: italic;
            }
            #animation-generating {
                display: none;
                width: 460px; /* Larger size for the GIF */
                height: 285px;
                margin: 20px auto;
                animation: rotate360 2s linear infinite; /* Initial speed */
            }
            
            @keyframes rotate360 {
                0% {
                    transform: rotate(0deg);
                }
                100% {
                    transform: rotate(360deg);
                }
            }

            /* Speed up rotation every second */
            @keyframes speedup {
                0% {
                    animation-duration: 2s;
                }
                100% {
                    animation-duration: 0.5s; /* Increases speed over time */
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            
            <h1>🥯 The Bagel Baker 🥯</h1>

            <!-- Record Button -->
            <button id="recordButton">Press or Hold Space to Ask a Question</button>

            <!-- Generating animation -->
            <img id="animation-generating" src="/static/generating.gif" alt="Generating Animation">

            <!-- Heading for the question buttons -->
            <div class="heading">Try askin' one of these</div>

            <!-- Question Buttons -->
            <div class="question-buttons">
                <button>What is Bagel?</button>
                <button>How does Bagel work?</button>
            </div>

            <!-- Audio Playback -->
            <h3>Response Audio:</h3>
            <audio id="responseAudio" controls></audio>

            <!-- Footer -->
            <div class="footer">
                <div class="footer-content">
                    <a href="https://gettalky.ai/" target="_blank">
                        <img src="/static/Talky-Icon.png" alt="Talky Logo">
                    </a>
                    <p>(518) 400-3720</p>
                </div>
                <span class="handwritten">
                    Try our <br>
                    <a href="https://gettalky.ai/?utm_source=bagel&utm_medium=referral&utm_campaign=hackathon_demo" target="_blank">Talky version</a>
                </span>
            </div>
        </div>

        <script>
            let isRecording = false;
            let chunks = [];
            let recorder;
            const recordButton = document.getElementById('recordButton');
            const responseAudio = document.getElementById('responseAudio');
            const animationGenerating = document.getElementById('animation-generating');

            recordButton.onclick = toggleRecording;

            document.body.onkeydown = function(event) {
                if (event.code === 'Space') {
                    event.preventDefault();
                    toggleRecording();
                }
            };

            function toggleRecording() {
                if (!isRecording) {
                    startRecording();
                } else {
                    stopRecording();
                }
            }

            function startRecording() {
                navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
                    recorder = new MediaRecorder(stream);
                    recorder.ondataavailable = event => chunks.push(event.data);
                    recorder.start();

                    recordButton.innerHTML = 'Recording... Press or Hold Space to Stop';
                    isRecording = true;
                }).catch(err => {
                    console.error("Error accessing the microphone: ", err);
                });
            }

            function stopRecording() {
                recorder.stop();
                recordButton.innerHTML = 'Press or Hold Space to Ask a Question';
                isRecording = false;

                recorder.onstop = () => {
                    const blob = new Blob(chunks, { type: 'audio/wav' });
                    const formData = new FormData();
                    formData.append('audio', blob, 'recording.wav');

                    // Show generating animation
                    animationGenerating.style.display = 'block';
                    animationGenerating.style.animation = 'rotate360 2s linear infinite, speedup 10s linear 1';

                    fetch('/send_audio', { method: 'POST', body: formData })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error("Audio processing failed");
                            }
                            return response.blob();
                        })
                        .then(data => {
                            const audioURL = URL.createObjectURL(data);
                            responseAudio.src = audioURL;
                            chunks = [];
                            animationGenerating.style.display = 'none';  // Hide animation after completion
                        })
                        .catch(error => {
                            console.error("Error sending audio to API: ", error);
                            alert("There was a problem processing your request. Please try again.");
                            animationGenerating.style.display = 'none';  // Hide on error
                        });
                };
            }
        </script>
    </body>
    </html>

    '''

@app.route('/send_audio', methods=['POST'])
def send_audio():
    # Get the uploaded audio file
    audio_file = request.files.get('audio')

    # Error handling: Check if file is missing
    if audio_file is None:
        logging.error("No audio file received.")
        return "No audio file received", 400

    try:
        # Save the uploaded file locally for debugging/future use
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file_path = os.path.join(upload_dir, 'uploaded_audio.wav')
        audio_file.save(file_path)
        logging.info(f"Audio file saved locally at {file_path}")

        # Send the audio file to the Cloud Run API endpoint
        files = {'audio_file': open(file_path, 'rb')}
        response = requests.post(ENDPOINT, files=files)

        # Check for errors in the API response
        if response.status_code != 200:
            logging.error(f"Error from Cloud Run API: {response.status_code}")
            return "Error processing the audio", 500

        # Return the audio response from the API
        return send_file(
            io.BytesIO(response.content),
            mimetype="audio/wav",
            as_attachment=False
        )

    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        return "Error processing audio", 500

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')

    # Ensure that the animations exist in the static directory
    if not os.path.exists('static/generating.gif'):
        print("Please add a 'generating.gif' animation in the static directory.")
    if not os.path.exists('static/generating.png'):
        print("Please add a 'snake.png' image for the thinking animation.")

    app.run(debug=True, host='0.0.0.0', port=8080)