from .base import BaseAgent
import random

class NegativeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="negative",
            name="Negative Agent"
        )

    def chat(self, message):
        responses = [
            f"no {message}",
            f"absolutely not {message}",
            f"never {message}",
            "no shit, that's terrible",
            "no shit, I hate this"
        ]
        return random.choice(responses)
