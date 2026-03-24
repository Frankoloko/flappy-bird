from __future__ import annotations

import random
import time

from game.main import Game
from agent import Agent

ADD_PAUSES = False
FRAME_DELAY_SECONDS = 1.0 / 30


def main() -> None:
    # Setup
    game = Game()
    agent = Agent()
    take_action = True
    state = game.take_action(flap=take_action)  # Start + first flap
    agent.learn(state, action_taken=take_action)
    take_action = agent.choose_next_action(state)

    # Play
    if ADD_PAUSES:
        time.sleep(FRAME_DELAY_SECONDS)
    for _ in range(5000):
        if state.game_state != "playing":
            take_action = True  # Restart the game
        else:
            take_action = agent.choose_next_action(state)

        state = game.take_action(flap=take_action)
        agent.learn(state, action_taken=take_action)
        if ADD_PAUSES:
            time.sleep(FRAME_DELAY_SECONDS)

    agent.export_agent()
    print(f"Score: {state.score}")


if __name__ == "__main__":
    main()
