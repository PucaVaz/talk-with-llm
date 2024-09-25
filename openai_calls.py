from openai import OpenAI
from pydub import AudioSegment
import simpleaudio as sa
import io
import time
from dotenv import load_dotenv
import os
import re

# Load environment variables from a .env file
load_dotenv()

# Access environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def play_audio(audio_data):
    try:
        # Load audio data from bytes as MP3
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
        
        # Export audio segment to raw audio data buffer
        raw_audio_data = audio_segment.raw_data
        
        # Get audio parameters
        sample_rate = audio_segment.frame_rate
        sample_width = audio_segment.sample_width
        channels = audio_segment.channels
        
        # Play the audio buffer using simpleaudio
        play_obj = sa.play_buffer(
            raw_audio_data,
            num_channels=channels,
            bytes_per_sample=sample_width,
            sample_rate=sample_rate,
        )
        
        # Wait for playback to finish before returning
        play_obj.wait_done()
    except Exception as e:
        print(f"An error occurred while playing audio: {e}")

class TTSGenerator:
    def __init__(self, client, tts_model="tts-1", voice="alloy", speed=1.25):
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
            

class GPTTTSPlayer:
    def __init__(self, client, gpt_model="gpt-4o-mini", tts_generator=None):
        """
        A class to interactively chat with GPT and generate TTS audio for the responses.
        """
        self.client = client
        self.gpt_model = gpt_model
        self.text_buffer = ""
        self.punctuation_marks = {".", "!", "?"}
        self.sentence_endings = re.compile(r'(?<=[.!?])\s+')

        # Initialize TTSGenerator
        if tts_generator is None:
            self.tts_generator = TTSGenerator(client)
        else:
            self.tts_generator = tts_generator

    def chat(self, prompt="Tell me the history of Brazil"):
        # Start the GPT chat completion stream
        stream = self.client.chat.completions.create(
            model=self.gpt_model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=28,
        )

        # Process the GPT completion stream and generate TTS for each sentence
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                self.text_buffer += content  # Accumulate the content in the text buffer
                print(f"Accumulated Text Buffer: {self.text_buffer}")
                
                # Check for complete sentences in the text buffer
                sentences = self.sentence_endings.split(self.text_buffer)
                # The last element may be an incomplete sentence
                for sentence in sentences[:-1]:
                    sentence = sentence.strip()
                    if sentence:
                        # Send the complete sentence to the TTS API
                        self.process_sentence(sentence)
                # The last element is either empty or an incomplete sentence
                self.text_buffer = sentences[-1]

        # After the stream ends, handle any remaining text
        remaining_text = self.text_buffer.strip()
        if remaining_text:
            self.process_sentence(remaining_text)
        self.text_buffer = ""

    def process_sentence(self, sentence):
        # Use the TTSGenerator to generate and play the sentence
        self.tts_generator.generate_and_play(sentence)

if __name__ == "__main__":
    # Initialize the OpenAI client in the main section
    client = OpenAI()

    # Initialize TTSGenerator separately if needed
    tts_generator = TTSGenerator(client, tts_model="tts-1", voice="alloy", speed=1.25)

    # Create an instance of GPTTTSPlayer with the initialized client and TTSGenerator
    player = GPTTTSPlayer(client, tts_generator=tts_generator)

    # Provide a prompt or ask the user for input
    prompt = input("Enter your prompt: ")

    # Start the chat
    player.chat(prompt)