from .base import BaseAgent

class NegativeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="negative",
            name="Negative Agent"
        )

    def chat(self, message):
        return f"no, {message}"
