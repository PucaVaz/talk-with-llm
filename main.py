from openai import OpenAI
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from speech_to_text.recognizer import AudioTranscriber
from gpt_generator.prompt_generation import GPTTTSPlayer
from audio.listen_and_process import AudioProcessor
from tts_generator import TTSGenerator
from conversation_manager import ConversationManager
conversation_history = ""

def main():
    client = OpenAI()

    # Create an instance of AudioTranscriber  
    transcriber = AudioTranscriber()

    # Initialize TTSGenerator
    tts_generator = TTSGenerator(client, tts_model="tts-1", voice="alloy", speed=1)

    # Create an instance of GPTTTSPlayer with the initialized client and TTSGenerator  
    player = GPTTTSPlayer(client, tts_generator=tts_generator)

    # Initialize the conversation manager
    conversation_manager = ConversationManager(system_prompt="You are a helpful assistant.", max_history=10)

    # Initialize the ProcessAudio class with the transcriber, player, and conversation manager
    processor = AudioProcessor(
        device_index=1,  # Set the appropriate audio device index, its is useful to use virtual audio devices
        conversation_manager=conversation_manager,
        transcriber=transcriber,
        player=player
    )
    
    # Start the listening and processing loop
    processor.listen_and_process()
    
if __name__ == '__main__':  
    main()