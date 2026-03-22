# Flappy Bird

## Setup

```bash
pip install -r requirements.txt
```

## Play normally

```bash
python main.py
```

**Controls:** Space or ↑ to flap · Left click to flap · Esc or close window to quit

## Step the game yourself (`next_action`)

Useful for scripts, tests, or agents: one frame per call, optional flap.

```python
from main import Game

game = Game()
state = game.next_action(flap=True)   # "playing" after title tap; then "ready" | "playing" | "gameover"
state = game.next_action(flap=False)  # one frame, no flap
```

`next_action` returns the state **after** that step. Title → first tap starts the round (same as space in normal play). After that, `flap=True` / `flap=False` is flap or glide for that frame. If the bird dies, the return is `"gameover"`; pass `flap=True` on a later step to go back to the title screen (tap to retry).

**Loop example:**

```python
from main import Game

game = Game()
state = game.next_action(flap=True)  # start + first flap
for _ in range(200):
    state = game.next_action(flap=False)
```

**Same game class, interactive loop:**

```python
from main import Game

Game().run()
```
