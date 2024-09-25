# AI-Powered Voice Assistant

This project implements an AI-powered voice assistant that can transcribe speech, process it using a language model, and respond with synthesized speech.

## Features

- Real-time audio recording with silence detection
- Speech-to-text transcription using Whisper model via Groq API
- Natural language processing using GPT model via OpenAI API
- Text-to-speech synthesis for AI responses
- Continuous conversation loop

## Components

1. `main.py`: The main script that orchestrates the voice assistant's functionality.
2. `speech_to_txt.py`: Handles audio transcription using the Groq API.
3. `openai_calls.py`: Manages interactions with the OpenAI API for language processing and text-to-speech synthesis.

## Setup

1. Clone the repository
2. Install required dependencies:
   ```
   pip install pyaudio wave numpy pydub openai simpleaudio python-dotenv groq
   ```
3. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key
     GROQ_API_KEY=your_groq_api_key
     ```

## Usage

Run the main script to start the voice assistant:

```
python main.py
```

The assistant will listen for your voice input, process it, and respond verbally.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
