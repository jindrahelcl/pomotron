from .openai import OpenAIAgent

class TradicniAgent(OpenAIAgent):
    def __init__(self):
        super().__init__("tradicni", "Tradicni Agent")
