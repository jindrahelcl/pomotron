from .prompt_loader import load_prompt
from .openai import OpenAIAgent

class AidaAgent(OpenAIAgent):
    def __init__(self):
        super().__init__("aida", "Aida Agent")

        # Initialize conversation history with the system message from file
        system_prompt = load_prompt("aida")
        # Initialize conversation history with the system message
        self.conversation_history = [
            {"role": "system", "content": system_prompt}
        ]

    def chat(self, message):
        if not self.client:
            return "Error: OpenAI API key not configured"

        try:
            # Add the user message to conversation history
            self.conversation_history.append({"role": "user", "content": message})

            # Send the full conversation history to the API
            response = self.client.responses.create(
                model="gpt-5-mini",
                input=self.conversation_history
            )

            # Get the assistant's response
            assistant_response = response.output_text.strip()

            # Add the assistant's response to conversation history
            self.conversation_history.append({"role": "assistant", "content": assistant_response})

            return assistant_response
        except Exception as e:
            return f"Error: {str(e)}"
