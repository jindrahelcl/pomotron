from .openai import OpenAIAgent

class DryGumAgent(OpenAIAgent):
    def __init__(self):
        super().__init__("dry_gum", "DryGum Agent")
