import os
import openai
from .base import BaseAgent

class StartAgent(BaseAgent):
    def __init__(self):
        super().__init__("start", "Start Agent", memory_size=10, enable_memory=True)
        self.client = None
        if os.environ.get('OPENAI_API_KEY'):
            self.client = openai.OpenAI(
                api_key=os.environ.get('OPENAI_API_KEY')
            )

    def chat(self, message):
        if not self.client:
            return "Error: OpenAI API key not configured"

        try:
            # Build messages with conversation history
            messages = [{"role": "system", "content": "You are a helpful assistant for a party management system. Keep responses concise and fun."}]
            
            # Add conversation history if available
            conversation_history = self.get_conversation_history()
            messages.extend(conversation_history)
            
            # Add current message
            messages.append({"role": "user", "content": message})

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            agent_response = response.choices[0].message.content.strip()
            
            # Add this exchange to memory
            self.add_to_memory(message, agent_response)
            
            return agent_response
        except Exception as e:
            error_response = f"Error: {str(e)}"
            # Still add to memory even if there's an error
            self.add_to_memory(message, error_response)
            return error_response
