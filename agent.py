import json
from datetime import datetime
import os
import random


class Agent:
    quality_table = {}
    alpha = 0.1  # Learning rate (increase or decrease the learning change by this amount)
    gamma = 0.99  # Future importance (how much to care about the future vs the current action)
    epsilon = 1.0  # Exploration chance (decreases over time as it learns more and more)
    agents_dir = "./agent_runs"
    agents_file_path = agents_dir + "/{}"

    min_relative_y = 9999
    max_relative_y = -9999
    min_bird_velocity = 9999
    max_bird_velocity = -9999
    min_next_pipe_distance_x = 9999
    max_next_pipe_distance_x = -9999

    def export_agent(self):
        os.makedirs(self.agents_dir, exist_ok=True)
        filename = f"agent_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        with open(self.agents_file_path.format(filename), 'w') as file:
            json.dump(self.quality_table, file, indent=4)

    def import_agent(self, filename: str):
        with open(self.agents_file_path.format(filename), 'r') as file:
            self.quality_table = json.load(file)

    def load_previous_agent(self):
        agents = sorted(os.listdir(self.agents_dir))
        if agents:
            self.import_agent(agents[-1])

    def learn(self, before_action_state, action_taken, after_action_state):
        """Learn 

        The logic essentially comes down to:
        new_action = old_action + adjustment
        Where adjustment == reward + (future_importants * new_action) - old_action

        """
        if after_action_state.game_state == "gameover":
            reward = -100  # Died
        else:
            reward = 1  # Survived one frame

        if after_action_state.score > before_action_state.score:
            reward += 10  # Successfully went through a pipe

        before_action_state_hash = self.get_state_hash(before_action_state)
        after_action_state_hash = self.get_state_hash(after_action_state)

        if before_action_state_hash not in self.quality_table:
            self.quality_table[before_action_state_hash] = [0, 0]
        if after_action_state_hash not in self.quality_table:
            self.quality_table[after_action_state_hash] = [0, 0]

        before_state = self.quality_table[before_action_state_hash]
        after_state = self.quality_table[after_action_state_hash]

        correction = reward + self.gamma * max(after_state) - before_state[action_taken]
        before_state[action_taken] += self.alpha * correction

        self.epsilon *= 0.99999
        self.epsilon = max(0.05, self.epsilon)
    
    def get_state_hash(self, state):
        if state.next_pipe_gap_center_y is not None:
            relative_y = int(state.bird_y - state.next_pipe_gap_center_y)
        else:
            relative_y = 0

        bird_velocity = int(round(state.bird_vel))
        next_pipe_distance_x = int(state.next_pipe_distance_x or 0)
        
        # Save the min and max values of each for logging later
        if relative_y < self.min_relative_y:
            self.min_relative_y = relative_y
        if relative_y > self.max_relative_y:
            self.max_relative_y = relative_y
        if bird_velocity < self.min_bird_velocity:
            self.min_bird_velocity = bird_velocity
        if bird_velocity > self.max_bird_velocity:
            self.max_bird_velocity = bird_velocity
        if next_pipe_distance_x < self.min_next_pipe_distance_x:
            self.min_next_pipe_distance_x = next_pipe_distance_x
        if next_pipe_distance_x > self.max_next_pipe_distance_x:
            self.max_next_pipe_distance_x = next_pipe_distance_x

        tuple_data = (
            self.bucket(relative_y, min_val=-500, max_val=310, num_buckets=30),
            self.bucket(bird_velocity, min_val=-16, max_val=19, num_buckets=10),
            self.bucket(next_pipe_distance_x, min_val=0, max_val=400, num_buckets=10),
        )
        return str(tuple_data)

    def choose_next_action(self, state):
        state_hash = self.get_state_hash(state)

        if random.random() < self.epsilon:
            # Weight exploration: flap only 30% of random actions, not 50%
            # Otherwise the bird just flies up and dies before learning anything
            return 1 if random.random() < 0.1 else 0

        if state_hash not in self.quality_table:
            return 1 if random.random() < 0.1 else 0

        return 1 if self.quality_table[state_hash][1] > self.quality_table[state_hash][0] else 0
    
    def bucket(self, value, min_val, max_val, num_buckets):
        value = max(min_val, min(max_val, value))
        ratio = (value - min_val) / (max_val - min_val)
        return min(int(ratio * num_buckets), num_buckets - 1)
