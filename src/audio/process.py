class ProcessAudio:
    def __init__(self, transcriber, player, conversation_manager):
        """Initialize the ProcessAudio class with dependencies."""
        self.transcriber = transcriber
        self.player = player
        self.conversation_manager = conversation_manager

    def process_audio_chunk(self, ogg_file_path):
        """Process the OGG audio file:
        - Transcribe it using AudioTranscriber.
        - Interact with GPT using GPTTTSPlayer.
        """
        # Transcribe the audio file
        transcription_text = self.transcriber.transcribe_audio(ogg_file_path)
        print("Transcription result:", transcription_text)

        # Check if transcription was successful
        if transcription_text:
            # Add user's message to conversation history
            self.conversation_manager.add_message("user", transcription_text)

            # Get conversation context messages
            context_messages = self.conversation_manager.get_conversation_context()

            # Interact with GPT and generate TTS audio
            assistant_response_text = self.player.chat(context_messages)

            # Add assistant's response to the conversation history
            self.conversation_manager.add_message("assistant", assistant_response_text)

            # Optionally, print the assistant's response
            print("Assistant response:", assistant_response_text)
        else:
            print("No transcription available.")


# How to use 
# Initialize the ProcessAudio class with the transcriber, player, and conversation manager
# process_audio
# process_audio.process_audio_chunk("path/to/audio.ogg") 