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
    RUNS = 10000
else:
    ADD_PAUSES = True
    RUNS = 100

def main() -> None:
    # Setup
    highest_score = -99
    flap_action_index = 1
    game = Game()
    agent = Agent()
    state = game.take_action(flap=flap_action_index)  # Start + first flap
    agent.learn(
        before_action_state=state,
        action_taken=flap_action_index,
        after_action_state=state,
    )
    take_action = agent.choose_next_action(state)

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
    if ADD_PAUSES:
        time.sleep(FRAME_DELAY_SECONDS)
    for _ in range(RUNS):
        if state.game_state != "playing":
            take_action = flap_action_index  # Restart the game
        else:
            take_action = agent.choose_next_action(state)

        state = game.take_action(flap=take_action)
        if state.score > highest_score:
            highest_score = state.score
        agent.learn(
            before_action_state=state,
            action_taken=flap_action_index,
            after_action_state=state,
        )
        if ADD_PAUSES:
            time.sleep(FRAME_DELAY_SECONDS)

    agent.export_agent()
    print(f"Highest Score: {highest_score}")


if __name__ == "__main__":
    main()
