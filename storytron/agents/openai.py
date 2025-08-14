import os
import openai
from .base import BaseAgent
from .prompt_loader import load_prompt


class OpenAIAgent(BaseAgent):
    def __init__(self, agent_id, name, memory_size=50, enable_memory=True, load_system_prompt=True, tts_engine='gtts', tts_voice=None):
        super().__init__(agent_id, name, memory_size, enable_memory, tts_engine, tts_voice)
        self._client = None

        if load_system_prompt:
            system_prompt = load_prompt(agent_id)
            self.conversation_history = [{"role": "system", "content": system_prompt}]
        else:
            self.conversation_history = []

    @property
    def client(self):
        if self._client is None and os.environ.get('OPENAI_API_KEY'):
            self._client = openai.OpenAI(
                api_key=os.environ.get('OPENAI_API_KEY'),
                timeout=45,
                max_retries=2  # Retry failed requests twice
            )
        return self._client

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
