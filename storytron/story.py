import json, os

STATE_FILE = os.environ.get('STORY_STATE_FILE', 'story_state.json')


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
        """Reset story to initial state: first agent active, all agents unsatisfied."""
        first_agent_id = list(self._agents.keys())[0]
        self.current_id = first_agent_id
        for agent in self._agents.values():
            agent.reset_satisfaction()
        self._save_state()

    def _decide_agent(self, current_id, agents, user_message, agent_reply, history=None):
        """Return the agent id to use for the NEXT turn.

        TODO: incorporate agent satisfaction flags, scoring, context analysis, etc.
        Currently NO-OP: keeps current agent.
        """
        return current_id

    # ---- persistence ----
    def _to_state(self):
        return {
            'current_id': self.current_id,
            'agents': {
                aid: {
                    'satisfied': getattr(a, 'satisfied', False)
                } for aid, a in self._agents.items()
            }
        }

    def _apply_state(self, data):
        if not data:
            return
        if 'current_id' in data and data['current_id'] in self._agents:
            self.current_id = data['current_id']
        agents_state = data.get('agents', {})
        for aid, st in agents_state.items():
            if aid in self._agents and 'satisfied' in st:
                setattr(self._agents[aid], 'satisfied', st['satisfied'])

    def _save_state(self):
        with open(STATE_FILE, 'w') as f:
            json.dump(self._to_state(), f)

    def load_state(self):
        with open(STATE_FILE, 'r') as f:
            data = json.load(f)
        self._apply_state(data)
