import pyaudio
import numpy as np

class Listen:
    def __init__(self, chunk_size=1024, format=pyaudio.paInt16, channels=1, rate=44100, silence_threshold=500, silence_duration=1):
        self.CHUNK = chunk_size
        self.FORMAT = format
        self.CHANNELS = channels
        self.RATE = rate
        self.SILENCE_THRESHOLD = silence_threshold
        self.SILENCE_DURATION = silence_duration

        self.p = pyaudio.PyAudio()
        self.input_device_index = self.__get_input_device_index() 
        self.stream = self.__open_stream()
        self.frames = []
        self.silent_chunks = 0
        self.speaking = False

    def __get_input_device_index(self):
        """Get the default input device or list devices and allow selection."""
        print("Available audio input devices:")
        input_device_index = None
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"Device {i}: {device_info['name']}")
                if input_device_index is None:  # Default to first input device
                    input_device_index = i
        return input_device_index

    def __open_stream(self):
        """Open a new audio stream using a specific input device."""
        return self.p.open(format=self.FORMAT,
                           channels=self.CHANNELS,
                           rate=self.RATE,
                           input=True,
                           frames_per_buffer=self.CHUNK,
                           input_device_index=self.input_device_index)  # Use the selected input device

    def __is_silent(self, data_chunk):
        """Check if the audio chunk is silent."""
        amplitude = np.frombuffer(data_chunk, dtype=np.int16)
        return np.abs(amplitude).mean() < self.SILENCE_THRESHOLD

    def record_until_silence(self):
        """Record audio until silence is detected."""
        print("Listening...")
        try:
            while True:
                try:
                    data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                except IOError as e:
                    print(f"An error occurred: {e}. Reopening stream.")
                    self.stream = self.__open_stream()
                    continue
                
                self.frames.append(data)
                silent = self.__is_silent(data)

                if silent:
                    if self.speaking:
                        self.silent_chunks += 1
                else:
                    self.speaking = True
                    self.silent_chunks = 0  # Reset silence counter when sound is detected

                if self.speaking and self.silent_chunks > (self.SILENCE_DURATION * self.RATE / self.CHUNK):
                    print("Silence detected. Stopping recording.")
                    break
                
        except KeyboardInterrupt:
            print("Recording interrupted by user.")
        finally:
            self.__stop()

        return b''.join(self.frames)

    def __stop(self):
        """Stop the recording stream and terminate PyAudio."""
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
