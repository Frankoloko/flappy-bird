import json
from datetime import datetime

class Agent:
    quality_table = {}

    def export_agent(self):
        agent_path = f"agent_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(agent_path, 'wb') as file:
            json.dump(self, f)

    def import_agent(self, agent_path: str):
        with open(agent_path, 'rb') as file:
            self.quality_table = json.load(f)

    def learn(self, state):
        state_hash = self.get_state_hash(state)
        if state_hash not in self.quality_table:
            self.quality_table[state_hash] = [0, 0]
        self.quality_table[state_hash] += 1
    
    def get_state_hash(self, state):
        return
