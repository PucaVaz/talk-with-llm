import re
from tts_generator import TTSGenerator

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

    def chat(self, messages):
        # Start the GPT chat completion stream
        stream = self.client.chat.completions.create(
            model=self.gpt_model,
            messages=messages,
            stream=True,
            max_tokens=28, 
        )

        assistant_response_text = ""
        # Process the GPT completion stream and generate TTS for each sentence
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                assistant_response_text += content
                self.text_buffer += content  # Accumulate the content in the text buffer
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

        return assistant_response_text

    def process_sentence(self, sentence):
        # Use the TTSGenerator to generate and play the sentence
        self.tts_generator.generate_and_play(sentence)