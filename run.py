from __future__ import annotations

import random
import time

from game.main import Game
from agent import Agent

HEADLESS = True

FRAME_DELAY_SECONDS = 1.0 / 30
ADD_PAUSES = True
if HEADLESS:
    ADD_PAUSES = False
    RUNS = 5000000
else:
    ADD_PAUSES = True
    RUNS = 100

def main() -> None:
    # Setup
    highest_score = -99
    flap_action_index = 1
    game = Game()
    agent = Agent()
    before_state = game.take_action(flap=flap_action_index)  # Start + first flap

    # The Q learning model works like this
    # 1. Get the current state
    # 2. Decide on the next action
    # 3. Take action and get the resulting state from that action
    # 4. Learn whether the action improved or worsened things, adjust your understanding

    # In Flappy's eyes it would be
    # 1. I'm currently right under the pipe gap
    # 2. Let's not flap right now
    # 3. That killed me
    # 4. Maybe next time I'm under the pipe gap I should try to flap instead
    # We adjust step 4 just slightly, otherwise you would over adjust, like a driver learning to ALWAYS turn left when a car comes from the right

    # Play
    for _ in range(RUNS):
        if before_state.game_state == "ready":
            take_action = flap_action_index  # Restart the game
        else:
            take_action = agent.choose_next_action(before_state)

        after_state = game.take_action(flap=take_action)

        # Only learn during actual gameplay
        if before_state.game_state == "playing":
            agent.learn(
                before_action_state=before_state,
                action_taken=take_action,
                after_action_state=after_state,
            )

        before_state = after_state

        if after_state.score > highest_score:
            highest_score = after_state.score
        if ADD_PAUSES:
            time.sleep(FRAME_DELAY_SECONDS)

    agent.export_agent()
    print(f"Highest Score: {highest_score}")


if __name__ == "__main__":
    main()
