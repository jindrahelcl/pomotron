class BaseAgent:
    def __init__(self, agent_id, name):
        self.agent_id = agent_id
        self.name = name
        self.satisfied = False

    def chat(self, message):
        raise NotImplementedError()

    # satisfaction helpers
    def mark_satisfied(self):
        self.satisfied = True

    def reset_satisfaction(self):
        self.satisfied = False

    def is_satisfied(self):
        return self.satisfied

    def to_dict(self):
        return {
            "id": self.agent_id,
            "name": self.name,
            "satisfied": self.satisfied
        }