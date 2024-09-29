import os
from groq import Groq

class AudioTranscriber:
    """
    A class to transcribe audio files to text using the Groq API.
    input: audio file path
    output: transcription text
    """
    def __init__(self, model="whisper-large-v3"):
        self.client = Groq()
        self.model = model

    def transcribe_audio(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"The file {filename} does not exist.")
        
        with open(filename, "rb") as file:
            transcription = self.client.audio.transcriptions.create(
                file=(filename, file.read()),
                model=self.model,
                response_format="verbose_json",
                language="pt"
            )
            return transcription.text

if __name__ == "__main__":
    # Example usage
    audio_file_path = os.path.join(os.path.dirname(__file__), "audio.m4a")
    transcriber = AudioTranscriber()

    try:
        transcription_text = transcriber.transcribe_audio(audio_file_path)
        print(transcription_text)
    except Exception as e:
        print(f"An error occurred: {e}")
