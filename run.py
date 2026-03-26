from __future__ import annotations
import time
import random
import time
from game.main import Game
from agent import Agent
from pprint import pprint

TRAIN_MODE = True

def main() -> None:
    # Setup
    log_info = {}
    start_time = time.time()
    frame_delay_seconds = 1.0 / 30
    highest_score = -99
    death_count = 0
    flap_action_index = 1
    game = Game(mute=True, enable_draw=not TRAIN_MODE)
    agent = Agent()
    agent.load_previous_agent()
    before_state = game.take_action(flap=flap_action_index)  # Start + first flap

    if TRAIN_MODE:
        add_pauses = False
        frames = 5000000 # 1min
        frames = 10000000 # 2min
    else:
        add_pauses = True
        frames = 1000  # 0min

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
    found_min_epsilon = False
    log_info["runs"] = []
    for current_frame in range(frames):
        # if not found_min_epsilon and agent.epsilon == 0.05:
        #     found_min_epsilon = True
        #     log_info["Reached Min Episilon On Frame"] = current_frame

        if before_state.game_state == "ready":
            take_action = flap_action_index  # Restart the game
        elif before_state.game_state == "gameover":
            take_action = flap_action_index  # Restart the game
            death_count += 1
            log_info["runs"].append({
                "run": death_count,
                "score": before_state.score,
            })
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
    log_info["Time Elapsed"] = f"{hours:02d}:{minutes:02d}"
    log_info["Deaths"] = death_count
    log_info["Highest Score"] = highest_score
    log_info["Ran Frames"] = frames
    log_info["Q Table Length"] = len(agent.quality_table)

    total_score = 0
    for run in log_info["runs"]:
        total_score += run["score"]
    log_info["Average Score Per Run"] = int(total_score / len(log_info["runs"]))

    del log_info["runs"]  # I just don't want to print this right now
    pprint(log_info, indent=4)


if __name__ == "__main__":
    for _ in range(5):
        main()
