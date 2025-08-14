from .openai import OpenAIAgent

class WasherWomanAgent(OpenAIAgent):
    def __init__(self):
        super().__init__("washer_woman", "WasherWoman Agent")
