import io
import wave
from pydub import AudioSegment
import pyaudio

class _AudioSaver:
    def __init__(self,channels=2, sample_format=pyaudio.paInt16, rate=44100):
        """
        Initialize the AudioSaver with audio parameters.

        :param channels: Number of audio channels.
        :param sample_format: Sample format (e.g., pyaudio.paInt16).
        :param rate: Sample rate in Hz.
        """
        self.channels = channels
        self.sample_format = sample_format
        self.rate = rate

    def save_audio_as_ogg(self, audio_data, filename):
        """
        Save the audio data as an OGG file.

        :param audio_data: Raw audio data.
        :param filename: Name for the saved file (without extension).
        :return: Path to the saved OGG file.
        """
        # Save the audio data to a WAV format in memory
        audio_wave = io.BytesIO()
        wf = wave.open(audio_wave, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(pyaudio.get_sample_size(self.sample_format))
        wf.setframerate(self.rate)
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

# Example usage:
# audio_saver = _AudioSaver(channels=2, sample_format=pyaudio.paInt16, rate=44100)
# audio_saver.save_audio_as_ogg(audio_data, 'output_filename')
