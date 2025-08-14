from .openai import OpenAIAgent

class ShotOutEyeAgent(OpenAIAgent):
    def __init__(self):
        super().__init__("shot_out_eye", "ShotOutEyeAgent Agent")
