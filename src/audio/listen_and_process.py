import io
import wave
import numpy as np
import pyaudio
from pydub import AudioSegment

# Audio recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Silence detection parameters
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 1  # in seconds



class AudioProcessor:
    def __init__(self, device_index, conversation_manager, transcriber, player):
        self.device_index = device_index
        self.conversation_manager = conversation_manager
        self.transcriber = transcriber
        self.player = player
        self.p = pyaudio.PyAudio()
        self.stream = None

    def list_audio_devices(self):
        """List available audio devices."""
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            print(f"Device {i}: {device_info['name']}")

    def is_silent(self, data_chunk):
        """Check if the audio chunk is silent."""
        amplitude = np.frombuffer(data_chunk, dtype=np.int16)
        return np.abs(amplitude).mean() < SILENCE_THRESHOLD

    def record_until_silence(self):
        """Record audio from the selected device until silence is detected."""
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  input_device_index=self.device_index,
                                  frames_per_buffer=CHUNK)

        print("Listening...")

        frames = []
        silent_chunks = 0
        speaking = False

        try:
            while True:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)

                silent = self.is_silent(data)

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
            self.stream.stop_stream()
            self.stream.close()

        return b''.join(frames)

    def save_audio_as_ogg(self, audio_data, filename):
        """Save the audio data as an OGG file."""
        audio_wave = io.BytesIO()
        wf = wave.open(audio_wave, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(audio_data)
        wf.close()
        audio_wave.seek(0)

        audio_segment = AudioSegment.from_wav(audio_wave)
        ogg_filename = f"./data/{filename}.ogg"
        audio_segment.export(ogg_filename, format='ogg')
        print(f"Audio saved as '{ogg_filename}'")
        return ogg_filename

    def process_audio_chunk(self, ogg_file_path):
        """Process the OGG audio file."""
        transcription_text = self.transcriber.transcribe_audio(ogg_file_path)
        print("Transcription result:", transcription_text)

        if transcription_text:
            self.conversation_manager.add_message("user", transcription_text)
            
            conversation_context = self.conversation_manager.get_conversation_context()

            # Generate a response from the assistant. The player will play the response by it self
            assistant_response_text = self.player.chat(conversation_context)

            # Add assistant's response to the conversation history
            self.conversation_manager.add_message("assistant", assistant_response_text)
            
            print("Assistant response:", assistant_response_text)
        else:
            print("No transcription available.")

    def listen_and_process(self):
        """Main loop to record, save, and process audio chunks."""
        while True:
            try:
                audio_data = self.record_until_silence()
                if audio_data:
                    ogg_file = self.save_audio_as_ogg(audio_data, filename='recorded_audio')
                    self.process_audio_chunk(ogg_file)
                    print("\nReady to listen again...\n")
                else:
                    print("No audio data captured.")
            except KeyboardInterrupt:
                print("Program terminated by user.")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Continuing to listen...\n")
