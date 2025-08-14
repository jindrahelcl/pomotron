import json, os
from agents.prompt_loader import load_prompt

STATE_FILE = os.environ.get('STORY_STATE_FILE', 'story_state.json')
DEFAULT_STATE_FILE = os.environ.get('DEFAULT_STORY_STATE_FILE', 'default_story_state.json')


class Story:

    def __init__(self, agents):
        if not agents:
            raise ValueError("At least one agent required")
        self._agents = {a.agent_id: a for a in agents}
        self.current_id = agents[0].agent_id

    @property
    def agents(self):
        return self._agents

    @property
    def active_agent(self):
        return self._agents[self.current_id]

    def to_listing(self):
        return [a.to_dict() for a in self._agents.values()]

    def set_active(self, agent_id):
        if agent_id not in self._agents:
            raise KeyError(agent_id)
        self.current_id = agent_id
        self._save_state()

    def chat(self, message):
        reply = self.active_agent.chat(message)
        new_id = self._decide_agent(self.current_id, self._agents, message, reply)
        if new_id in self._agents and new_id != self.current_id:
            self.current_id = new_id
            self._save_state()
        return reply

    def reset_story(self):
        """Reset story to default state from default_story_state.json."""
        with open(DEFAULT_STATE_FILE, 'r') as f:
            default_data = json.load(f)
        self._apply_state(default_data)
        self._save_state()

    def _decide_agent(self, current_id, agents, user_message, agent_reply, history=None):
        """ MAIN STORY PROGRESSION LOGIC, IMPLEMENT HERE (possibly refactor to a separate module what do I know...) """
        if current_id == 'default' and 'happy' in user_message.lower():
            agents['default'].mark_satisfied()
            agents['negative'].reset_satisfaction()
            return 'negative'
        elif current_id == 'negative' and agent_reply.lower().startswith('no shit'):
            agents['negative'].mark_satisfied()
            agents['default'].reset_satisfaction()
            return 'default'

        return current_id

    # ---- persistence ----
    def _to_state(self):
        agents_state = {}
        for aid, a in self._agents.items():
            agent_state = {
                'satisfied': getattr(a, 'satisfied', False),
                'tts_engine': getattr(a, 'tts_engine', 'gtts'),
                'tts_voice': getattr(a, 'tts_voice', 'cs')
            }
            # Add memory state if agent has memory enabled
            memory_state = a.get_memory_state()
            if memory_state:
                agent_state['memory'] = memory_state
            agents_state[aid] = agent_state

        return {
            'current_id': self.current_id,
            'agents': agents_state
        }

    def _apply_state(self, data):
        if not data:
            return
        if 'current_id' in data and data['current_id'] in self._agents:
            self.current_id = data['current_id']
        agents_state = data.get('agents', {})
        for aid, st in agents_state.items():
            if aid in self._agents:
                # Restore satisfaction state
                if 'satisfied' in st:
                    setattr(self._agents[aid], 'satisfied', st['satisfied'])
                # Restore TTS configuration
                if 'tts_engine' in st:
                    setattr(self._agents[aid], 'tts_engine', st['tts_engine'])
                if 'tts_voice' in st:
                    setattr(self._agents[aid], 'tts_voice', st['tts_voice'])
                # Restore memory state
                if 'memory' in st:
                    self._agents[aid].set_memory_state(st['memory'])

                # Update system prompt for OpenAI agents after satisfaction state is restored
                agent = self._agents[aid]
                if (hasattr(agent, 'load_system_prompt') and agent.load_system_prompt and
                    hasattr(agent, 'conversation_history') and agent.conversation_history and
                    agent.conversation_history[0]['role'] == 'system'):
                    system_prompt = load_prompt(agent.agent_id, agent.satisfied)
                    agent.conversation_history[0]['content'] = system_prompt

    def _save_state(self):
        with open(STATE_FILE, 'w') as f:
            json.dump(self._to_state(), f)

    def load_state(self):
        with open(STATE_FILE, 'r') as f:
            data = json.load(f)
        self._apply_state(data)
