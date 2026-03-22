from __future__ import annotations

import random
import time

from main import Game

# Pause between steps so you can follow the bird and pipes (seconds).
FRAME_DELAY_SECONDS = 1.0 / 30

# Each loop iteration: independent probability of flapping (0.0 = never, 1.0 = always).
RANDOM_FLAP_PROBABILITY = 0.01


def main() -> None:
    game = Game()
    game.next_action(flap=True)  # start + first flap
    time.sleep(FRAME_DELAY_SECONDS)
    for _ in range(200):
        should_flap = random.random() < RANDOM_FLAP_PROBABILITY
        game.next_action(flap=should_flap)
        time.sleep(FRAME_DELAY_SECONDS)


if __name__ == "__main__":
    main()
