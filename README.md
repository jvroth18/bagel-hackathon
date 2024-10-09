
# Conversational AI with Fine-tuned LLM and Google Cloud APIs

This repository contains code to build a fully functional conversational AI application that leverages a fine-tuned LLM from Bagel’s decentralized compute platform and Google Cloud's Speech-to-Text and Text-to-Speech APIs. The project is designed to handle customer service queries, taking audio input from the user, processing the input with the fine-tuned model, and generating a spoken response.

## Key Features

- **Front-end (Flask App)**: Captures microphone input, sends audio for processing, and plays AI-generated audio responses.
- **Back-end (FastAPI Service)**: Processes speech input, runs inference using a fine-tuned LLM model, and generates a spoken response using Google Cloud Text-to-Speech.
- **Fine-tuning on Bagel**: Easily fine-tune models with Bagel’s Bakery platform without worrying about managing infrastructure or deep technical configurations.
- **Cloud Deployment**: Supports deployment via Docker to platforms such as Google Cloud Run or Compute Engine for scalability and high availability.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or later
- BagelML package (`pip install bagelML`)
- Docker
- Google Cloud SDK (if deploying to Google Cloud)
- Flask, FastAPI, and other dependencies (listed in `requirements.txt`)

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/conversational-ai-llm.git
    cd conversational-ai-llm
    ```

2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up BagelML for fine-tuning models:
    - Follow the steps in the article to generate your API key from Bagel.
    - Fine-tune your model using the provided Python scripts for dataset uploading and model fine-tuning.

4. Configure Google Cloud APIs:
    - Enable **Speech-to-Text** and **Text-to-Speech** APIs on your Google Cloud project.
    - Set up authentication with a service account JSON file and configure environment variables:
      ```bash
      export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account-key.json"
      ```

### Usage

#### Running Locally

To test the application locally, run the Flask front-end and FastAPI back-end on your machine:

1. Start the FastAPI service (backend):
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

2. Start the Flask front-end:
    ```bash
    python app.py
    ```

3. Open your browser and navigate to `http://localhost:5000`. You can start interacting with the conversational AI by recording your voice.


#### API Endpoints

- **POST /chat**: Send an audio file to the backend for inference and get an audio response.
    - **Request**: Audio file (WAV format)
    - **Response**: Audio (WAV format) with the AI-generated response

### Fine-Tuning with Bagel

1. Upload your dataset to Bagel:
    ```python
    import bagel
    client = bagel.Client()
    client.create_asset(payload, api_key)
    client.file_upload(file_path, asset_id, api_key)
    ```

2. Fine-tune your model:
    ```python
    client.fine_tune(title, user_id, asset_id, file_name, base_model, epochs=3, learning_rate=0.01)
    ```

### Cloud Components

- **Google Cloud Speech-to-Text**: Transcribes user audio input into text.
- **Bagel’s LLM Model**: Processes the transcribed text and generates a response.
- **Google Cloud Text-to-Speech**: Converts the generated text into speech, providing the user with a spoken response.

## File Structure

```
.
├── app
│   ├── finetuned-model
│   │   ├── adapter_config.json
│   │   ├── adapter_model.safetensors
│   │   ├── generation_config.json
│   │   ├── special_tokens_map.json
│   │   ├── tokenizer_config.json
│   │   └── tokenizer.json
│   ├── main.py
│   └── requirements.txt
├── ui
│   ├── static
│   │   ├── generating.gif
│   │   └── Talky-Icon.png
│   └── frontend.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! If you'd like to improve this project, feel free to fork the repository and submit a pull request. Please make sure to follow the [contribution guidelines](CONTRIBUTING.md).

## Acknowledgements

- BagelML for providing the decentralized platform for fine-tuning LLMs.
- Google Cloud for offering robust Speech-to-Text and Text-to-Speech APIs.
- All open-source contributors who have made the development of this project possible.
