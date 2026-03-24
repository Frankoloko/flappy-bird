import json
from datetime import datetime
import os
import random



class Agent:
    quality_table = {}
    alpha = 0.1  # Learning rate (increase or decrease the learning change by this amount)
    gamma = 0.99  # Future importance (how much to care about the future vs the current action)
    epsilon = 1.0  # Exploration chance (decreases over time as it learns more and more)

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

    def learn(self, state, action_taken):
        state_hash = self.get_state_hash(state)
        
        # Initialize key
        if state_hash not in self.quality_table:
            self.quality_table[state_hash] = [0, 0]

        if state.game_state == "gameover":
            reward = -100
        else:
            reward = +1

        self.quality_table[state_hash][action_taken] += self.alpha * (
            reward +
            self.gamma *
            max(self.quality_table[state_hash])
            - self.quality_table[state_hash][action_taken]
        )

        # Decrease epsilon
        self.epsilon *= 0.995
        self.epsilon = max(0.05, self.epsilon)  # epsilon min is 0.05
    
    def get_state_hash(self, state):
        tuple_data = (
            int(state.bird_y),
            int(state.next_pipe_gap_center_y or 0),
            int(state.next_pipe_distance_x or 0),
        )
        return str(tuple_data)

    def choose_next_action(self, state):
        state_hash = self.get_state_hash(state)

        # Check if we should explore random options a bit
        if random.random() < self.epsilon:
            return random.choice([0, 1])

        # Don't explore random options, do what we know is best already
        if self.quality_table[state_hash][0] > self.quality_table[state_hash][1]:
            action_index = 1
        else:
            action_index = 0

        # Return the index of the action to take [X, Y]
        return action_index
