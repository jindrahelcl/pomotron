import os
import openai
from .base import BaseAgent

class OpenAIAgent(BaseAgent):
    def __init__(self, agent_id, name, memory_size=20, enable_memory=True):
        super().__init__(agent_id, name, memory_size, enable_memory)
        self._client = None

    @property
    def client(self):
        if self._client is None and os.environ.get('OPENAI_API_KEY'):
            self._client = openai.OpenAI(
                api_key=os.environ.get('OPENAI_API_KEY'),
                timeout=20.0
            )
        return self._client