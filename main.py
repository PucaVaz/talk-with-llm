from openai import OpenAI
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from speech_to_text.recognizer import AudioTranscriber
from gpt_generator.prompt_generation import GPTTTSPlayer
from audio.listen_and_process import listen_and_process
from tts_generator import TTSGenerator
from audio.listen import Listen
from audio.process import ProcessAudio
from conversation_manager import ConversationManager
conversation_history = ""

def main():
    client = OpenAI()

    # Create an instance of AudioTranscriber  
    transcriber = AudioTranscriber()

    # Initialize TTSGenerator
    tts_generator = TTSGenerator(client, tts_model="tts-1", voice="alloy", speed=1.25)

    # Create an instance of GPTTTSPlayer with the initialized client and TTSGenerator  
    player = GPTTTSPlayer(client, tts_generator=tts_generator)

    # Initialize the conversation manager
    conversation_manager = ConversationManager(system_prompt="You are a helpful assistant.", max_history=10)

    # Initialize the ProcessAudio class with the transcriber, player, and conversation manager
    process_audio = ProcessAudio(transcriber, player, conversation_manager)
    
    # Initialize the Listen class
    listen = Listen()

    # Start the main loop
    listen_and_process(listen, process_audio)
# Initialize the transcriber and GPT player at the beginning

if __name__ == '__main__':  
    main()