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

    def export_agent(self):
        os.makedirs(self.agents_dir, exist_ok=True)
        filename = f"agent_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        with open(self.agents_file_path.format(filename), 'w') as file:
            json.dump(self.quality_table, file, indent=4)

    def import_agent(self, filename: str):
        with open(self.agents_file_path.format(filename), 'r') as file:
            self.quality_table = json.load(file)

    def load_previous_agent(self):
        agents = os.listdir(self.agents_dir)
        self.import_agent(agents[-1])

    def learn(self, before_action_state, action_taken, after_action_state):
        """Learn 

        The logic essentially comes down to:
        new_action = old_action + adjustment
        Where adjustment == reward + (future_importants * new_action) - old_action

        """
        if after_action_state.game_state == "gameover":
            reward = -100
            if before_action_state.next_pipe_gap_center_y is not None:
                dist = before_action_state.bird_y - before_action_state.next_pipe_gap_center_y
                if dist < -80:  # Died flying too high
                    reward -= 50
                elif dist > 80:  # Died flying too low
                    reward -= 50
        elif after_action_state.next_pipe_gap_center_y is not None:
            dist = abs(after_action_state.bird_y - after_action_state.next_pipe_gap_center_y)
            reward = max(1, 10 - int(dist / 20))
            if dist > 100:
                reward -= 5
        else:
            reward = 1

        if after_action_state.score > before_action_state.score:
            reward += 10  # Was 50 — too high, was teaching the agent to spam flap

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

        # self.epsilon *= 0.99999
        # self.epsilon = max(0.05, self.epsilon)
    
    def get_state_hash(self, state):
        if state.next_pipe_gap_center_y is not None:
            relative_y = int(state.bird_y - state.next_pipe_gap_center_y)
        else:
            relative_y = 0

        tuple_data = (
            relative_y,
            int(round(state.bird_vel)),
            int(state.next_pipe_distance_x or 0),
        )
        return str(tuple_data)

    def choose_next_action(self, state):
        state_hash = self.get_state_hash(state)

        # if random.random() < self.epsilon:
        #     # Weight exploration: flap only 30% of random actions, not 50%
        #     # Otherwise the bird just flies up and dies before learning anything
        #     return 1 if random.random() < 0.1 else 0

        if state_hash not in self.quality_table:
            return 1 if random.random() < 0.1 else 0

        return 1 if self.quality_table[state_hash][1] > self.quality_table[state_hash][0] else 0