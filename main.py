import pyaudio
import wave
import numpy as np
from pydub import AudioSegment
import io
from openai import OpenAI

# Local imports
from speech_to_txt import AudioTranscriber
from openai_calls import GPTTTSPlayer, TTSGenerator
from conversation_manager import ConversationManager

# Audio recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Silence detection parameters
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 1  # in seconds

def is_silent(data_chunk):
    """Check if the audio chunk is silent."""
    amplitude = np.frombuffer(data_chunk, dtype=np.int16)
    return np.abs(amplitude).mean() < SILENCE_THRESHOLD

def record_until_silence():
    """Record audio until user stops speaking."""
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Listening...")

    frames = []
    silent_chunks = 0
    speaking = False

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

            silent = is_silent(data)

            if silent:
                if speaking:
                    silent_chunks += 1
            else:
                speaking = True
                silent_chunks = 0  # Reset silence counter when sound is detected

            # Stop if silence has been detected for enough duration
            if speaking and silent_chunks > (SILENCE_DURATION * RATE / CHUNK):
                print("Silence detected. Stopping recording.")
                break
    except KeyboardInterrupt:
        print("Recording interrupted by user.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    return b''.join(frames)

def save_audio_as_ogg(audio_data, filename):
    """
    Save the audio data as an OGG file.

    :param audio_data: Raw audio data.
    :param filename: Name for the saved file (without extension).
    :return: Path to the saved OGG file.
    """
    # Save the audio data to a WAV format in memory
    audio_wave = io.BytesIO()
    wf = wave.open(audio_wave, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(audio_data)
    wf.close()
    audio_wave.seek(0)

    # Read the WAV data with pydub
    audio_segment = AudioSegment.from_wav(audio_wave)

    # Export to OGG format
    ogg_filename = f"{filename}.ogg"
    audio_segment.export(ogg_filename, format='ogg')
    print(f"Audio saved as '{ogg_filename}'")
    return ogg_filename

# Initialize the conversation history
conversation_history = ""

def process_audio_chunk(ogg_file_path):  
    """  
    Process the OGG audio file:  
    - Transcribe it using AudioTranscriber.  
    - Interact with GPT using GPTTTSPlayer.  
    """  
    # Use the pre-initialized Transcriber, Player, and ConversationManager  
    global transcriber, player, conversation_manager

    # Transcribe the audio file  
    transcription_text = transcriber.transcribe_audio(ogg_file_path)  
    print("Transcription result:", transcription_text)

    # Check if transcription was successful  
    if transcription_text:  
        # Add user's message to conversation history
        conversation_manager.add_message("user", transcription_text)

        # Get conversation context messages
        context_messages = conversation_manager.get_conversation_context()

        # Interact with GPT and generate TTS audio  
        assistant_response_text = player.chat(context_messages)

        # Add assistant's response to the conversation history
        conversation_manager.add_message("assistant", assistant_response_text)
        
        # Optionally, print the assistant's response
        print("Assistant response:", assistant_response_text)
    else:  
        print("No transcription available.")
        
def listen_and_process():
    """Main loop to record, save, and process audio chunks."""
    while True:
        try:
            # Record audio until silence is detected
            audio_data = record_until_silence()
            if audio_data:
                # Save audio as OGG file
                ogg_file = save_audio_as_ogg(audio_data, filename='recorded_audio')

                # Call the processing function with the OGG file
                process_audio_chunk(ogg_file)

                print("\nReady to listen again...\n")
            else:
                print("No audio data captured.")

        except KeyboardInterrupt:
            print("Program terminated by user.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Continuing to listen...\n")

# Initialize the transcriber and GPT player at the beginning
if __name__ == '__main__':  
    # Initialize the OpenAI client  
    client = OpenAI()

    # Create an instance of AudioTranscriber  
    transcriber = AudioTranscriber()

    # Initialize TTSGenerator
    tts_generator = TTSGenerator(client, tts_model="tts-1", voice="alloy", speed=1.25)

    # Create an instance of GPTTTSPlayer with the initialized client and TTSGenerator  
    player = GPTTTSPlayer(client, tts_generator=tts_generator)

    # Initialize the conversation manager
    conversation_manager = ConversationManager(system_prompt="You are a helpful assistant.", max_history=10)

    listen_and_process()