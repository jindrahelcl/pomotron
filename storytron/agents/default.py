from .base import BaseAgent

class DefaultAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="default",
            name="Default Agent",
            enable_memory=False  # Simple rule-based agent doesn't need memory
        )

    def chat(self, message):
        return f"yes, {message}"
