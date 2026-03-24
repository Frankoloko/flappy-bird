from __future__ import annotations

import random
import time

from game.main import Game
from agent import Agent

FRAME_DELAY_SECONDS = 1.0 / 30
RANDOM_FLAP_PROBABILITY = 0.01


def main() -> None:
    # Setup
    game = Game()
    agent = Agent()
    take_action = True
    state = game.next_action(flap=take_action)  # Start + first flap
    agent.learn(state, action_taken=take_action)

    # Play
    time.sleep(FRAME_DELAY_SECONDS)
    for _ in range(1000):
        if state.game_state != "playing":
            take_action = True  # Restart the game
        else:
            take_action = agent.choose_next_action(state)

        state = game.next_action(flap=take_action)
        agent.learn(state, action_taken=take_action)
        time.sleep(FRAME_DELAY_SECONDS)

    agent.export_agent()


if __name__ == "__main__":
    main()
