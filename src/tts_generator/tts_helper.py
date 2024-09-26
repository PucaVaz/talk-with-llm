from pydub import AudioSegment
import simpleaudio as sa
import io

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