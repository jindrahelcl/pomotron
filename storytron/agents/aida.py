import os
import openai
from .base import BaseAgent

class AidaAgent(BaseAgent):
    def __init__(self):
        super().__init__("aida", "Aida Agent")
        self.client = None
        if os.environ.get('OPENAI_API_KEY'):
            self.client = openai.OpenAI(
                api_key=os.environ.get('OPENAI_API_KEY')
            )

    def chat(self, message):
        if not self.client:
            return "Error: OpenAI API key not configured"

        try:
            response = self.client.responses.create(
                model="gpt-5-mini",
                input=[
                    {"role": "system", "content": "You are a helpful assistant for a party management system. Keep responses concise and fun."},
                    {"role": "user", "content": message}
                ]
            )
            return response.output_text.strip()
        except Exception as e:
            return f"Error: {str(e)}"
