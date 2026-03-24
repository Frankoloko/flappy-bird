import json
from datetime import datetime
import os

class Agent:
    quality_table = {}

    def export_agent(self):
        agents_dir = "./agent_runs"
        os.makedirs(agents_dir, exist_ok=True)
        filename = f"agent_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        agent_path = f"./{agents_dir}/{filename}"
        with open(agent_path, 'w') as file:
            json.dump(self.quality_table, file, indent=4)

    def import_agent(self, agent_path: str):
        with open(agent_path, 'r') as file:
            self.quality_table = json.load(file)

    def learn(self, state):
        state_hash = self.get_state_hash(state)
        if state_hash not in self.quality_table:
            self.quality_table[state_hash] = [0, 0]
        # self.quality_table[state_hash] = [0, 1]
    
    def get_state_hash(self, state):
        tuple_data = (
            int(state.bird_y),
            int(state.next_pipe_gap_center_y or 0),
            int(state.next_pipe_distance_x or 0),
        )
        return str(tuple_data)