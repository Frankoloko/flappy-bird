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
    state = game.next_action(flap=True)  # start + first flap
    agent.learn(state)

    time.sleep(FRAME_DELAY_SECONDS)
    for _ in range(100):
        if state.game_state != "playing":
            should_flap = True
        else:
            should_flap = random.random() < RANDOM_FLAP_PROBABILITY
        state = game.next_action(flap=should_flap)
        agent.learn(state)
        time.sleep(FRAME_DELAY_SECONDS)

    agent.export_agent()


if __name__ == "__main__":
    main()
