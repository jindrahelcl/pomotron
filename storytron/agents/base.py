class BaseAgent:
    def __init__(self, agent_id, name, description):
        self.agent_id = agent_id
        self.name = name
        self.description = description

    def chat(self, message):
        raise NotImplementedError()

    def to_dict(self):
        return {
            "id": self.agent_id,
            "name": self.name,
            "description": self.description
        }
