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

g = Game()
g.next_action(True)   # from title: starts + flaps once; while playing: flap + one step
g.next_action(False)  # one frame, no flap
```

Title → first tap starts the round (same as space in normal play). After that, `True` / `False` is flap or glide for that frame.

**Loop example:**

```python
from main import Game

g = Game()
g.next_action(True)  # start + first flap
for _ in range(200):
    g.next_action(False)
```

**Same game class, interactive loop:**

```python
from main import Game

Game().run()
```
