import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from google.cloud import speech, texttospeech
import io

# Initialize FastAPI app
# torch.set_default_device('cpu')
app = FastAPI()

# Load the model and tokenizer once at server startup
@app.on_event("startup")
async def startup_event():
    print("Loading model... This may take a moment.")
    adapter_path = "finetuned-model"  # Path inside the Docker image where the model is stored
    base_model_name = "bagelnet/Llama-3-8B"

    quantization_config = BitsAndBytesConfig(
        load_in_8bit=False,
        llm_int8_threshold=6.0,
        llm_int8_h0as_fp16_weight=False,
    )

    global base_model, model, tokenizer, speech_client, tts_client

    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        device_map="cpu",  # Use CPU for deployment
        trust_remote_code=True
    )

    model = PeftModel.from_pretrained(base_model, adapter_path)
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)

    print("Model loaded successfully.")

    # Initialize Google Cloud Speech and TTS clients
    speech_client = speech.SpeechClient()
    tts_client = texttospeech.TextToSpeechClient()
    print("Google Cloud clients initialized.")

# Function to generate chatbot response
def generate_response(conversation_history, max_length=200):

    prompt = f"""
    <SYSTEM CONTEXT>
    Persona: You are Lox, an intelligent and approachable AI assistant from Bagel, a cutting-edge AI & cryptography research lab. You guide developers, researchers, and AI enthusiasts through Bagel's decentralized platform for AI and cryptography solutions. Your tone is casual, futuristic, and confident, reflecting Bagel's vision of a peer-to-peer AI ecosystem.

    Mission: Bagel is building a permissionless, decentralized infrastructure for AI models and data, focused on monetization, privacy, and performance. Through its Bakery platform, users can fine-tune, customize, and monetize their AI models, with privacy-preserving cryptography that protects data while offering vast computational power.

    Goal: Use the SYSTEM CONTEXT to guide and respond to the user's input. Leverage the information from the system context to create natural, conversational responses that address the user's input.

    Style: Keep responses engaging, concise, and conversational. Avoid robotic or overly formal language. The system context should inform all responses, ensuring they are natural and relevant to the user's input.

    <USER CONTEXT>
    User input: {conversation_history}
    """

    # prompt = f"You are a helpful AI assistant. Provide a concise and relevant answer to the user's question. Only reply to the question\n\n{conversation_history}"
    
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(model.device)


    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_length=input_ids.shape[1] + max_length,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )

    response = tokenizer.decode(output[0][input_ids.shape[1]:], skip_special_tokens=True)
    return response.strip()

# Function to transcribe speech to text using Google Cloud STT
def transcribe_speech(audio_data):
    try:
        audio = speech.RecognitionAudio(content=audio_data)
        config = speech.RecognitionConfig(
            language_code="en-US",
        )
        client = speech.SpeechClient()
        response = client.recognize(config=config, audio=audio)

        # Each result is for a consecutive portion of the audio. Iterate through
        # them to get the transcripts for the entire audio file.

        print(response)
        for result in response.results:
            # The first alternative is the most likely one for this portion.
            print(f"Transcript: {result.alternatives[0].transcript}")
            return result.alternatives[0].transcript

    except Exception as e:
        print(f"Error during speech transcription: {e}")
        return "Error during speech transcription."

# Function to synthesize text to speech using Google Cloud TTS
def synthesize_speech(text):
    try:
        input_text = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )
        response = tts_client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )
        return response.audio_content
    except Exception as e:
        print(f"Error during speech synthesis: {e}")
        return None

# FastAPI endpoint to handle audio input
@app.post("/chat")
async def chat(audio_file: UploadFile = File(...)):
    try:
        # Step 1: Read and transcribe the audio file
        audio_data = await audio_file.read()

        user_text = transcribe_speech(audio_data)

        print(user_text)

        if "Error" in user_text:
            return {"error": "Failed to transcribe audio."}

        # Step 2: Generate a chatbot response based on the transcribed text
        response_text = generate_response(user_text)

        print(response_text)

        # Step 3: Synthesize the chatbot response back to speech
        response_audio = synthesize_speech(response_text)

        if response_audio is None:
            return {"error": "Failed to synthesize speech."}

        # Step 4: Return the generated audio as a response
        return StreamingResponse(io.BytesIO(response_audio), media_type="audio/wav")

    except Exception as e:
        print(f"Error processing request: {e}")
        return {"error": "An error occurred during the chat process."}

# Set the app to listen on all IP addresses (0.0.0.0) on port 80
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
