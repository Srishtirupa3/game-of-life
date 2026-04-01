# 🧬 Conway's Game of Life

![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=flat&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-Canvas-E34F26?style=flat&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-Backdrop--filter-1572B6?style=flat&logo=css3&logoColor=white)
![No Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen?style=flat)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat)

> An infinite cellular automaton that lives and breathes as your website background —
> built with zero dependencies using vanilla JavaScript and HTML Canvas.

---

## 👀 Preview

The simulation runs silently behind your page content. Cells are born, survive, and die
according to Conway's four rules. Move your mouse across the page to seed new life.
Still-life patterns dissolve after 8 seconds, keeping the grid perpetually dynamic.

```
  Background (canvas z-index: 0)          Content (z-index: 1)
  ░ ░░  ░  ░░ ░   ░░░  ░  ░░  ░
    ░░   ┌──────────────────────┐  ░
  ░   ░░ │  Your page content  │    ░░
    ░    │  sits here, always  │  ░
  ░░   ░ │  readable on top    │░░    ░
         └──────────────────────┘
  ░  ░░   ░░  ░   ░  ░░   ░   ░  ░░  ░
```

---

## ✨ Features

- **Auto-running** — starts immediately on page load with a randomised grid
- **Fully interactive** — the background reacts to your mouse in real time
- **Age-kill system** — still-lifes and stable patterns dissolve after ~8 seconds, preventing frozen dead zones
- **Two-phase death animation** — cells pre-dim as they age, then fade out slowly on death
- **Rebirth prevention** — age-killed positions are blocked from immediately reforming
- **Auto-respawn** — if the population crashes, new life is seeded automatically
- **Responsive** — canvas resizes with the window and preserves existing cells
- **Zero dependencies** — pure HTML, CSS, and vanilla JS; no build step, no npm

---

## 🚀 Quick Start

```bash
git clone https://github.com/Srishtirupa3/game-of-life.git
cd game-of-life
open index.html        # macOS
# Windows / Linux: just double-click index.html
```

That's it. No server, no install, no build.

---

## 🕹️ Controls

| Input | Action |
|---|---|
| Move mouse | Seeds a subtle trail of live cells wherever you go |
| Left click | Bursts a dense cluster of cells at the cursor |
| Left drag | Continuously paints cells — draw freely |
| Right drag | Erases cells in a radius |

> All interactions are captured at the `document` level, so they work even when the mouse is hovering over page content sitting on top of the canvas.

---

## 🧬 The Rules

Every cell looks at its 8 neighbours. All cells update simultaneously each generation.

| Current State | Live Neighbours | Next State | Reason |
|---|---|---|---|
| Alive | < 2 | Dies | Underpopulation |
| Alive | 2 or 3 | Survives | Stable |
| Alive | > 3 | Dies | Overpopulation |
| Dead | exactly 3 | Born | Reproduction |

Despite only four rules, the simulation produces wildly complex emergent behaviour —
gliders, oscillators, still-lifes, and unpredictable chaotic patterns.

---

## ⚙️ How It Works

<details>
<summary><strong>Grid representation</strong></summary>

The grid is a JavaScript `Set` of `"row,col"` string keys. Only **alive cells** are stored — memory and CPU scale with the live population, not the total grid size. An 80×60 grid with 500 live cells only processes those 500 cells per tick, not 4,800.

</details>

<details>
<summary><strong>Simulation tick (O(alive cells))</strong></summary>

Each tick, we iterate every alive cell and increment a neighbour-count for each of its 8 surrounding positions. After one pass, every candidate cell has a count. We then apply the four rules in a single loop over that count map — no scanning of dead space.

</details>

<details>
<summary><strong>Age-kill system</strong></summary>

Each live cell tracks `cellAge` — how many consecutive generations it has been alive. Once `cellAge >= MAX_CELL_AGE` (80 ticks = 8 seconds), the cell is forcibly killed. Critically, killed positions are added to a `blocked` map with a 30-tick cooldown, preventing the simulation from immediately regrowing the same still-life at those coordinates.

</details>

<details>
<summary><strong>Death animation</strong></summary>

Cells go through two visual phases before disappearing:
1. **Pre-death dimming** — from tick 48 onward (60% of max age), `liveOpacity()` linearly dims the cell to 25% of full brightness. You see the cell ghosting before it dies.
2. **Post-death fade** — age-killed cells are placed in a `dying` map with `FADE_TICKS_AGE = 50` render frames (~800 ms), giving a slow, visible dissolve. Natural deaths use a quicker 12-frame fade.

</details>

<details>
<summary><strong>Render loop</strong></summary>

Rendering runs at the browser's native refresh rate (~60 fps) via `requestAnimationFrame`. The simulation ticks every `TICK_INTERVAL = 100 ms` independently — so the animation is always smooth even when the simulation is busy.

</details>

---

## 📁 Project Structure

```
game-of-life/
├── index.html               # Page shell — canvas element + demo content layout
├── style.css                # Fixed canvas behind content; hero backdrop; hint bar
├── gol.js                   # Everything: grid logic, renderer, interactions, age system
└── python_game/
    ├── main.py              # Pygame desktop app — full simulation with HUD & controls
    └── test_game_of_life.py # 31 unit tests covering all rules and known patterns
```

`gol.js` is structured in clear sections:

```
Config → Helpers → Grid logic → Seeding → Mouse influence → Rendering → Game loop → Init
```

---

## 🔧 Customisation

Every tunable value is at the top of `gol.js`:

```javascript
const CELL_SIZE         = 12;            // pixels per cell (smaller = denser grid)
const TICK_INTERVAL     = 100;           // ms between ticks (lower = faster sim)
const BASE_OPACITY      = 0.50;          // max cell brightness 0–1
const INIT_DENSITY      = 0.22;          // fraction of cells alive at start
const MAX_CELL_AGE      = 80;            // ticks before stagnant cell is killed
const AGE_DIM_START     = 48;            // tick at which pre-death dimming begins
const BLOCKED_TTL       = 30;            // ticks a dead position resists rebirth
const CELL_COLOR        = '0, 210, 110'; // RGB — swap for any colour theme
```

**Example themes:**

| Theme | `CELL_COLOR` | `background` in CSS |
|---|---|---|
| Green on black (default) | `'0, 210, 110'` | `#080808` |
| Blue on dark | `'50, 150, 255'` | `#05080f` |
| Amber on black | `'255, 180, 0'` | `#080808` |
| White on dark | `'220, 220, 220'` | `#0a0a0a` |

---

## 🐍 Python Version

This project began as a full desktop app in Python + Pygame before being ported to the web.
The Python version lives in a separate directory and features:

- Pygame window with live HUD (generation, FPS, population)
- Keyboard controls: `Space` pause · `N` step · `R` random · `C` clear · `G` grid toggle · `↑↓` speed
- Mouse draw and erase support
- **31 unit tests** covering all four rules, known patterns (blinker, glider, beehive, toad, block), and edge cases

---

## 🌐 Embed in Your Own Site

Drop these three lines into any existing page to use the simulation as its background:

```html
<!-- 1. Add to <head> -->
<link rel="stylesheet" href="style.css" />

<!-- 2. Add as first child of <body> -->
<canvas id="gol-canvas"></canvas>

<!-- 3. Add before </body> -->
<script src="gol.js"></script>
```

---

## 🏗️ Browser Support

| Browser | Support |
|---|---|
| Chrome / Edge | ✅ Full |
| Firefox | ✅ Full |
| Safari | ✅ Full |
| Mobile browsers | ⚠️ Renders correctly; touch interactions not yet mapped |

---

## 📜 License

MIT — use it, modify it, ship it.

---

<p align="center">Built with curiosity and four simple rules.</p>
