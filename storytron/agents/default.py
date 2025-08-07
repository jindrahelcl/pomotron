from .base import BaseAgent

class DefaultAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="default",
            name="Default Agent",
            description="Echo agent"
        )

    def chat(self, message):
        return f"yes, {message}"
