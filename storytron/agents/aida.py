from .openai import OpenAIAgent

class AidaAgent(OpenAIAgent):
    def __init__(self):
        super().__init__("aida", "Aida Agent")
