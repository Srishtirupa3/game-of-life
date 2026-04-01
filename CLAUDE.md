# CLAUDE.md — Game of Life

Project context and instructions for Claude Code working in this repo.

## What This Project Is

Conway's Game of Life implemented in two forms:
1. **JS website background** — interactive simulation behind a webpage (`index.html`, `style.css`, `gol.js`)
2. **Python desktop app** — pygame window with full controls (`python_game/main.py`)

## Running Things

```bash
# Open the website
open index.html

# Run the Python game
python3 python_game/main.py

# Run the Python tests
python3 python_game/test_game_of_life.py
# or
python3 -m pytest python_game/test_game_of_life.py -v
```

## Project Structure

```
game-of-life/
├── index.html               # Page shell and demo content
├── style.css                # Canvas as fixed background, hero backdrop, hint bar
├── gol.js                   # Full JS simulation engine
├── CLAUDE.md                # This file
├── README.md
└── python_game/
    ├── main.py              # Pygame desktop game
    └── test_game_of_life.py # 31 unit tests (mocks pygame for headless run)
```

## Key Decisions Already Made

### JS (`gol.js`)
- Grid is a `Set` of `"row,col"` strings — only alive cells stored
- `cellAge` map tracks generations alive per cell
- `blocked` map prevents rebirth at age-killed positions for 30 ticks — this is what stops still-lifes from immediately reforming
- `dying` map holds post-death fade ticks — age-killed cells use `FADE_TICKS_AGE=50` (slow), natural deaths use `FADE_TICKS_NORMAL=12` (fast)
- Pre-death dimming starts at `AGE_DIM_START=48` (60% of `MAX_CELL_AGE=80`)
- Canvas is `z-index:0`, `pointer-events:none` — mouse events listened on `document` so they fire over content too
- **No full-screen vignette** — it was painting above the canvas due to a CSS stacking context bug (`z-index:-1` inside a `z-index:1` parent). Hero has its own `backdrop-filter` instead.

### Python (`main.py`)
- Grid is a `set` of `(row, col)` tuples
- `get_neighbors()` returns a list of 8 positions
- `next_generation()` uses a neighbor count dict — O(alive cells)

## Tunable Constants (gol.js)

```js
const CELL_SIZE         = 12;
const TICK_INTERVAL     = 100;    // ms — lower is faster
const BASE_OPACITY      = 0.50;
const INIT_DENSITY      = 0.22;
const MAX_CELL_AGE      = 80;     // ticks = 8 seconds
const AGE_DIM_START     = 48;     // when pre-death dimming begins
const BLOCKED_TTL       = 30;     // ticks a position resists rebirth
const CELL_COLOR        = '0, 210, 110'; // RGB
```

## GitHub

- **Repo:** https://github.com/Srishtirupa3/game-of-life
- **Account:** Srishtirupa3 (shreya.vyas5@gmail.com)
- `gh` CLI is at `/opt/homebrew/bin/gh`

## Conventions

- Plan first, implement after approval
- Test Python logic before adding new features to `main.py`
- Keep `gol.js` as a single file — no splitting into modules
- Don't add a build step or npm — keep it zero-dependency
