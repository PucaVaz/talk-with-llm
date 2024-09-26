import time
from tts_generator.tts_helper import play_audio

class TTSGenerator:
    def __init__(self, client, tts_model="tts-1", voice="alloy", speed=1):
        """
        A class dedicated to generating TTS audio from text.
        """
        self.client = client
        self.tts_model = tts_model
        self.voice = voice
        self.speed = speed
        self.first_time = time.time()

    def generate_and_play(self, text):
        """
        Generate TTS audio for the given text and play it.
        """
        text_time = time.time()

        # Print the time difference since the last TTS call
        print(f"Time since last TTS request: {text_time - self.first_time:.2f} seconds")

        # Generate TTS audio for the text
        tts_response = self.client.audio.speech.create(
            model=self.tts_model,
            voice=self.voice,
            input=text,
            speed=self.speed,
            response_format='mp3',  # Specify MP3 format
        )

        end_time = time.time()

        # Print how long it took to generate the audio
        print(f"TTS generation time: {end_time - text_time:.2f} seconds")

        # Update the first_time for the next cycle
        self.first_time = end_time

        # Check if the response contains audio content
        if hasattr(tts_response, 'content'):
            # Extract and play the audio data from the response
            audio_data = tts_response.content
            play_audio(audio_data)
        else:
            print("No audio content received from TTS API.")
            

