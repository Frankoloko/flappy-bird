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

    def learn(self, before_action_state, action_taken, after_action_state):
        """Learn 

        The logic essentially comes down to:
        new_action = old_action + adjustment
        Where adjustment == reward + (future_importants * new_action) - old_action

        """
        before_action_state_hash = self.get_state_hash(before_action_state)
        after_action_state_hash = self.get_state_hash(after_action_state)
        
        # Initialize key
        if before_action_state_hash not in self.quality_table:
            self.quality_table[before_action_state_hash] = [0, 0]

        if before_action_state.game_state == "gameover":
            reward = -100
        else:
            reward = +1

        before_state = self.quality_table[before_action_state_hash]
        after_state = self.quality_table[after_action_state_hash]

        # correction = reward + future_importance + (before or after correctness)
        correction = reward + self.gamma * max(after_state) - before_state[action_taken]

        # new_action = learning_rate * correction
        before_state[action_taken] += self.alpha * correction

        # Decrease epsilon
        self.epsilon *= 0.995
        self.epsilon = max(0.05, self.epsilon)  # epsilon min is 0.05
    
    def get_state_hash(self, state):
        tuple_data = (
            int(state.bird_y / 100),
            int((state.bird_vel or 0)),
            int((state.next_pipe_gap_center_y or 0) / 100),
            int((state.next_pipe_distance_x or 0) / 10),
        )
        return str(tuple_data)

    def choose_next_action(self, state):
        state_hash = self.get_state_hash(state)

        # Check if we should explore random options a bit
        if random.random() < self.epsilon:
            return random.choice([0, 1])

        if state_hash not in self.quality_table:
            return random.choice([0, 1])

        # Don't explore random options, do what we know is best already
        if self.quality_table[state_hash][0] < self.quality_table[state_hash][1]:
            action_index = 1
        else:
            action_index = 0

        # Return the index of the action to take [X, Y]
        return action_index
