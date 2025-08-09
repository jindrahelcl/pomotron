import os
import openai
from .base import BaseAgent

class WasherWomanAgent(BaseAgent):
    def __init__(self):
        super().__init__("washer_woman", "WasherWoman Agent")
        self.client = None
        # Initialize conversation history with the system message
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful assistant for a party management system. Keep responses concise and fun."}
        ]

        if os.environ.get('OPENAI_API_KEY'):
            self.client = openai.OpenAI(
                api_key=os.environ.get('OPENAI_API_KEY')
            )

    def chat(self, message):
        if not self.client:
            return "Error: OpenAI API key not configured"

        try:
            # Add the user message to conversation history
            self.conversation_history.append({"role": "user", "content": message})

            # Send the full conversation history to the API
            response = self.client.responses.create(
                model="gpt-5-mini",
                input=self.conversation_history
            )

            # Get the assistant's response
            assistant_response = response.output_text.strip()

            # Add the assistant's response to conversation history
            self.conversation_history.append({"role": "assistant", "content": assistant_response})

            return assistant_response
        except Exception as e:
            return f"Error: {str(e)}"

