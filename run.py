from __future__ import annotations

import random
import time

from game.main import Game
from agent import Agent

FRAME_DELAY_SECONDS = 1.0 / 30
RANDOM_FLAP_PROBABILITY = 0.01


def main() -> None:
    game = Game()
    agent = Agent()
    take_action = True
    state = game.next_action(flap=take_action)  # start + first flap
    agent.learn(state, action_taken=take_action)

    time.sleep(FRAME_DELAY_SECONDS)
    for _ in range(100):
        if state.game_state != "playing":
            take_action = True
        else:
            take_action = random.random() < RANDOM_FLAP_PROBABILITY
        state = game.next_action(flap=take_action)
        agent.learn(state, action_taken=take_action)
        time.sleep(FRAME_DELAY_SECONDS)

    agent.export_agent()


if __name__ == "__main__":
    main()
