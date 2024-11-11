import asyncio
import websockets
import json
import pyaudio
import wave
import base64
import logging
import os
from dotenv import load_dotenv
import numpy as np
import io

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 24000

# Silence detection parameters
SILENCE_THRESHOLD = 100  # Adjust based on microphone sensitivity
SILENCE_DURATION = 1  # in seconds

# WebSocket configuration
WS_URL = "wss://api.openai.com/v1/realtime"
MODEL = "gpt-4o-realtime-preview-2024-10-01"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is not set. Please set it in your environment variables.")
    exit(1)

class RealtimeClient:
    def __init__(self):
        logger.info("Initializing RealtimeClient")
        self.ws = None
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.audio_buffer = b''

    async def connect(self):
        logger.info(f"Connecting to WebSocket: {WS_URL}")
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
        self.ws = await websockets.connect(f"{WS_URL}?model={MODEL}", extra_headers=headers)
        logger.info("Successfully connected to OpenAI Realtime API")

    async def send_event(self, event):
        logger.debug(f"Sending event: {event}")
        await self.ws.send(json.dumps(event))
        logger.debug("Event sent successfully")

    async def receive_events(self):
        logger.info("Starting to receive events")
        try:
            async for message in self.ws:
                logger.debug(f"Received raw message: {message}")
                event = json.loads(message)
                await self.handle_event(event)
        except websockets.exceptions.ConnectionClosedOK:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"An error occurred while receiving events: {e}")

    async def handle_event(self, event):
        event_type = event.get("type")
        logger.info(f"Handling event of type: {event_type}")

        if event_type == "error":
            logger.error(f"Error event received: {event['error']['message']}")
        elif event_type == "response.text.delta":
            logger.debug(f"Text delta received: {event['delta']}")
            print(event["delta"], end="", flush=True)
        elif event_type == "response.audio.delta":
            logger.debug(f"Audio delta received, length: {len(event['delta'])}")
            audio_data = base64.b64decode(event["delta"])
            self.audio_buffer += audio_data
        elif event_type == "response.audio.done":
            logger.info("Audio response complete, playing audio")
            self.play_audio(self.audio_buffer)
            self.audio_buffer = b''
        else:
            logger.info(f"Received other event type: {event_type}")

    def is_silent(self, data_chunk):
        """Check if the audio chunk is silent."""
        amplitude = np.frombuffer(data_chunk, dtype=np.int16)
        return np.abs(amplitude).mean() < SILENCE_THRESHOLD

    async def listen_and_process_audio(self):
        """Continuously listen to the microphone and process audio when speech is detected."""
        logger.info("Starting audio input stream")
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK)
        logger.info("Listening for speech...")

        frames = []
        silent_chunks = 0
        speaking = False

        try:
            while True:
                data = await asyncio.get_event_loop().run_in_executor(None, self.stream.read, CHUNK, False)
                frames.append(data)

                silent = self.is_silent(data)

                if silent:
                    if speaking:
                        silent_chunks += 1
                    else:
                        # Not speaking yet, reset frames
                        frames = []
                else:
                    speaking = True
                    silent_chunks = 0  # Reset silence counter when sound is detected

                # Stop if silence has been detected for enough duration
                if speaking and silent_chunks > (SILENCE_DURATION * RATE / CHUNK):
                    logger.info("Silence detected. Processing audio.")
                    audio_data = b''.join(frames)
                    await self.send_audio(audio_data)
                    frames = []
                    speaking = False
                    silent_chunks = 0
                    logger.info("Ready to listen again.")
                    logger.info("Listening for speech...")
        except Exception as e:
            logger.error(f"An error occurred during audio recording: {e}")
        finally:
            self.stream.stop_stream()
            self.stream.close()
            logger.info("Audio input stream stopped")

    async def send_audio(self, audio_data):
        logger.info(f"Preparing to send audio data, size: {len(audio_data)} bytes")

        base64_audio = base64.b64encode(audio_data).decode('utf-8')
        logger.debug(f"Audio encoded to base64, length: {len(base64_audio)}")

        event = {
            "type": "input_audio_buffer.append",
            "audio": base64_audio
        }
        await self.send_event(event)
        logger.debug("Audio buffer appended, committing buffer")
        await self.send_event({"type": "input_audio_buffer.commit"})
        logger.debug("Audio buffer committed, creating response")
        await self.send_event({"type": "response.create"})

    def play_audio(self, audio_data):
        logger.info(f"Playing audio, size: {len(audio_data)} bytes")
        stream = self.p.open(format=FORMAT,
                             channels=CHANNELS,
                             rate=RATE,
                             output=True)
        stream.write(audio_data)
        stream.stop_stream()
        stream.close()
        logger.debug("Audio playback complete")

    async def run(self):
        logger.info("Starting RealtimeClient run")
        await self.connect()

        # Create tasks for receiving events and listening to audio
        receive_task = asyncio.create_task(self.receive_events())
        listen_task = asyncio.create_task(self.listen_and_process_audio())

        logger.info("Sending initial message to start the conversation")
        await self.send_event({
            "type": "response.create",
            "response": {
                "modalities": ["text", "audio"],
                "instructions": "You are a helpful AI assistant. Respond to the user's messages.",
            }
        })

        try:
            await asyncio.gather(receive_task, listen_task)
        except Exception as e:
            logger.error(f"An error occurred in run: {e}")
        finally:
            logger.info("Ending conversation and closing connection")
            receive_task.cancel()
            listen_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass
            try:
                await listen_task
            except asyncio.CancelledError:
                pass
            await self.ws.close()
            self.p.terminate()

async def main():
    logger.info("Starting main function")
    client = RealtimeClient()
    try:
        await client.run()
    except Exception as e:
        logger.error(f"An error occurred in main: {e}")
    finally:
        logger.info("Main function completed")

if __name__ == "__main__":
    logger.info("Script started")
    asyncio.run(main())
    logger.info("Script completed")
