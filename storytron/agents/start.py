from .openai import OpenAIAgent

class StartAgent(OpenAIAgent):
    def __init__(self):
        super().__init__("start", "Start Agent")
