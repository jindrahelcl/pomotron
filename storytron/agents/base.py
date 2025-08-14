from collections import deque
from datetime import datetime

class BaseAgent:
    def __init__(self, agent_id, name, memory_size=20, enable_memory=True):
        self.agent_id = agent_id
        self.name = name
        self.satisfied = False

        # Memory system
        self.enable_memory = enable_memory
        self.memory_size = memory_size
        self.conversation_memory = deque(maxlen=memory_size) if enable_memory else None

    def chat(self, message):
        raise NotImplementedError()

    # Memory management
    def add_to_memory(self, user_message, agent_response):
        """Add a conversation exchange to memory"""
        if not self.enable_memory or self.conversation_memory is None:
            return

        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "agent": agent_response
        }
        self.conversation_memory.append(exchange)

    def get_conversation_history(self, include_system_prompt=True):
        """Get conversation history formatted for OpenAI API"""
        if not self.enable_memory or not self.conversation_memory:
            return []

        messages = []
        for exchange in self.conversation_memory:
            messages.append({"role": "user", "content": exchange["user"]})
            messages.append({"role": "assistant", "content": exchange["agent"]})

        return messages

    def get_memory_summary(self):
        """Get a text summary of recent conversation for context"""
        if not self.enable_memory or not self.conversation_memory:
            return ""

        summary_parts = []
        recent_exchanges = list(self.conversation_memory)[-5:]  # Last 5 exchanges

        for exchange in recent_exchanges:
            summary_parts.append(f"User: {exchange['user']}")
            summary_parts.append(f"Agent: {exchange['agent']}")

        return "\n".join(summary_parts)

    def clear_memory(self):
        """Clear conversation memory"""
        if self.enable_memory and self.conversation_memory is not None:
            self.conversation_memory.clear()

    def get_memory_state(self):
        """Get memory state for persistence"""
        if not self.enable_memory or self.conversation_memory is None:
            return None

        return {
            "memory_size": self.memory_size,
            "enable_memory": self.enable_memory,
            "conversation_memory": list(self.conversation_memory)
        }

    def set_memory_state(self, memory_state):
        """Restore memory state from persistence"""
        if not memory_state:
            return

        self.memory_size = memory_state.get("memory_size", 20)
        self.enable_memory = memory_state.get("enable_memory", True)

        if self.enable_memory:
            self.conversation_memory = deque(maxlen=self.memory_size)
            for exchange in memory_state.get("conversation_memory", []):
                self.conversation_memory.append(exchange)

    # satisfaction helpers
    def mark_satisfied(self):
        self.satisfied = True

    def reset_satisfaction(self):
        self.satisfied = False

    def is_satisfied(self):
        return self.satisfied

    def to_dict(self):
        result = {
            "id": self.agent_id,
            "name": self.name,
            "satisfied": self.satisfied,
            "memory_enabled": self.enable_memory
        }

        if self.enable_memory and self.conversation_memory is not None:
            result["memory_count"] = len(self.conversation_memory)
            result["memory_size"] = self.memory_size

        return result