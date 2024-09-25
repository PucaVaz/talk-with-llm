import json
from typing import List, Dict

class ConversationManager:
    def __init__(self, system_prompt: str = "", max_history: int = 10):
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.conversation_history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        """Add a new message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})
        
        # Trim history if it exceeds max_history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def get_conversation_context(self) -> List[Dict[str, str]]:
        """Get the full conversation context including the system prompt."""
        context = [{"role": "system", "content": self.system_prompt}] if self.system_prompt else []
        context.extend(self.conversation_history)
        return context

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def set_system_prompt(self, prompt: str):
        """Set or update the system prompt."""
        self.system_prompt = prompt

    def save_conversation(self, filename: str):
        """Save the conversation history to a file."""
        with open(filename, 'w') as f:
            json.dump({
                "system_prompt": self.system_prompt,
                "history": self.conversation_history
            }, f, indent=2)

    def load_conversation(self, filename: str):
        """Load a conversation history from a file."""
        with open(filename, 'r') as f:
            data = json.load(f)
            self.system_prompt = data.get("system_prompt", "")
            self.conversation_history = data.get("history", [])

    def get_last_message(self) -> Dict[str, str]:
        """Get the last message in the conversation history."""
        return self.conversation_history[-1] if self.conversation_history else {}

    def summarize_conversation(self) -> str:
        """Generate a summary of the conversation."""
        # This is a placeholder. In a real implementation, you might use an AI model to generate a summary.
        return f"Conversation with {len(self.conversation_history)} messages."