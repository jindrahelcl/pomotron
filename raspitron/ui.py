import sys

class RaspiTRONUI:
    def __init__(self):
        pass

    def log_action(self, action: str):
        print(f"[LOG] {action}", file=sys.stderr)

    def print_message(self, message: str):
        print(message)

    def print_prompt(self):
        print("> ", end="", flush=True)
