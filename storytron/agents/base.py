from collections import deque
from datetime import datetime
import warnings

class BaseAgent:
    # TTS engines and their supported voices
    TTS_ENGINES = {
        'festival': ['krb', 'dita', 'machac', 'ph', 'mbrola'],
        'gtts': ['default'],
        'openai': ['alloy', 'ash', 'ballad', 'coral', 'echo', 'fable', 'nova', 'onyx', 'sage', 'shimmer'],
        'gemini': [
            'Zephyr', 'Puck', 'Charon', 'Kore', 'Fenrir', 'Leda',
            'Orus', 'Aoede', 'Callirrhoe', 'Autonoe', 'Enceladus', 'Iapetus',
            'Umbriel', 'Algieba', 'Despina', 'Erinome', 'Algenib', 'Rasalgethi',
            'Laomedeia', 'Achernar', 'Alnilam', 'Schedar', 'Gacrux', 'Pulcherrima',
            'Achird', 'Zubenelgenubi', 'Vindemiatrix', 'Sadachbia', 'Sadaltager', 'Sulafat'
        ]
    }

    def __init__(self, agent_id, name, memory_size=50, enable_memory=True, tts_engine='gtts', tts_voice=None):
        self.agent_id = agent_id
        self.name = name
        self.satisfied = False

        # TTS configuration
        if tts_engine not in self.TTS_ENGINES:
            warnings.warn(f"Invalid TTS engine '{tts_engine}'. Using default 'gtts' instead. Valid engines: {list(self.TTS_ENGINES.keys())}")
            self.tts_engine = 'gtts'
        else:
            self.tts_engine = tts_engine

        # Set default voice if none provided
        if tts_voice is None:
            tts_voice = self.TTS_ENGINES[self.tts_engine][0]

        if tts_voice not in self.TTS_ENGINES.get(self.tts_engine, []):
            default_voice = self.TTS_ENGINES[self.tts_engine][0]
            warnings.warn(f"Invalid TTS voice '{tts_voice}' for engine '{self.tts_engine}'. Using default '{default_voice}' instead. Valid voices for {self.tts_engine}: {self.TTS_ENGINES[self.tts_engine]}")
            self.tts_voice = default_voice
        else:
            self.tts_voice = tts_voice        # Memory system
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
        state = {
            "tts_engine": self.tts_engine,
            "tts_voice": self.tts_voice
        }

        if not self.enable_memory or self.conversation_memory is None:
            return state

        state.update({
            "memory_size": self.memory_size,
            "enable_memory": self.enable_memory,
            "conversation_memory": list(self.conversation_memory)
        })

        return state

    def set_memory_state(self, memory_state):
        """Restore memory state from persistence"""
        if not memory_state:
            return

        # Restore TTS configuration
        self.tts_engine = memory_state.get("tts_engine", "gtts")
        self.tts_voice = memory_state.get("tts_voice", None)

        # Validate TTS configuration
        if self.tts_engine not in self.TTS_ENGINES:
            warnings.warn(f"Invalid TTS engine '{self.tts_engine}' loaded from state. Using default 'gtts' instead. Valid engines: {list(self.TTS_ENGINES.keys())}")
            self.tts_engine = "gtts"

        # Set default voice if none provided or if current voice is invalid
        if self.tts_voice is None:
            self.tts_voice = self.TTS_ENGINES[self.tts_engine][0]
        elif self.tts_voice not in self.TTS_ENGINES.get(self.tts_engine, []):
            default_voice = self.TTS_ENGINES[self.tts_engine][0]
            warnings.warn(f"Invalid TTS voice '{self.tts_voice}' for engine '{self.tts_engine}' loaded from state. Using default '{default_voice}' instead. Valid voices for {self.tts_engine}: {self.TTS_ENGINES[self.tts_engine]}")
            self.tts_voice = default_voice

        self.memory_size = memory_state.get("memory_size", 20)
        self.enable_memory = memory_state.get("enable_memory", True)

        if self.enable_memory:
            self.conversation_memory = deque(maxlen=self.memory_size)
            for exchange in memory_state.get("conversation_memory", []):
                self.conversation_memory.append(exchange)

    def get_supported_voices(self):
        """Get list of supported voices for the current TTS engine"""
        return self.TTS_ENGINES.get(self.tts_engine, [])

    def set_tts_config(self, engine, voice):
        """Set TTS engine and voice configuration"""
        if engine in self.TTS_ENGINES:
            self.tts_engine = engine
            if voice in self.TTS_ENGINES[engine]:
                self.tts_voice = voice
            else:
                self.tts_voice = self.TTS_ENGINES[engine][0]
        else:
            raise ValueError(f"Unsupported TTS engine: {engine}")

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
            "memory_enabled": self.enable_memory,
            "tts_engine": self.tts_engine,
            "tts_voice": self.tts_voice
        }

        if self.enable_memory and self.conversation_memory is not None:
            result["memory_count"] = len(self.conversation_memory)
            result["memory_size"] = self.memory_size

        return result