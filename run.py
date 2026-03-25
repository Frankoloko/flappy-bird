from __future__ import annotations
import time
import random
import time
from game.main import Game
from agent import Agent

TRAIN_MODE = True

def main() -> None:
    # Setup
    start_time = time.time()
    frame_delay_seconds = 1.0 / 30
    highest_score = -99
    death_count = 0
    flap_action_index = 1
    game = Game()
    agent = Agent()
    agent.load_previous_agent()
    before_state = game.take_action(flap=flap_action_index)  # Start + first flap

    if TRAIN_MODE:
        add_pauses = False
        frames = 10000 # 18s
        frames = 100000 # 2min
        frames = 500000 # 11min
        # frames = 1000000 # 22min
    else:
        add_pauses = True
        frames = 100

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
    printed = False
    for current_frame in range(frames):
        if not printed and agent.epsilon == 0.05:
            printed = True
            print(f"Reached min epsilon: {current_frame}")

        if before_state.game_state == "ready":
            take_action = flap_action_index  # Restart the game
        elif before_state.game_state == "gameover":
            take_action = flap_action_index  # Restart the game
            death_count += 1
        elif before_state.game_state == "playing":
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

        if add_pauses:
            time.sleep(frame_delay_seconds)

    agent.export_agent()

    elapsed = int(time.time() - start_time)
    hours = elapsed // 3600
    minutes = (elapsed % 3600) // 60
    print(f"Time elapsed: {hours:02d}:{minutes:02d}")

    print(f"Deaths: {death_count}")
    print(f"Highest score: {highest_score}")


if __name__ == "__main__":
    main()
