# Conway's Game of Life
# Step 1+2: Grid logic  |  Step 3: Rendering  |  Step 4+5: Controls  |  Step 6: UI polish

import pygame
import sys
import random

# ── Constants ───────────────────────────────────────────
CELL_SIZE = 12
COLS      = 80
ROWS      = 60
WIDTH     = COLS * CELL_SIZE
HEIGHT    = ROWS * CELL_SIZE

FPS_MIN   = 2
FPS_MAX   = 60
FPS_STEP  = 2

# Colors
COLOR_BG        = (15,  15,  15)
COLOR_GRID      = (30,  30,  30)
COLOR_ALIVE     = (0,   200, 100)
COLOR_HOVER     = (0,   200, 100,  60)   # transparent green tint
COLOR_HUD_TEXT  = (200, 200, 200)
COLOR_PAUSED    = (220, 80,  80)
COLOR_RUNNING   = (80,  220, 120)
COLOR_DIM       = (90,  90,  90)

# HUD panel dimensions
HUD_W = 160
HUD_H = 88


# ── Grid logic ──────────────────────────────────────────

def get_neighbors(row, col):
    return [
        (row - 1, col - 1), (row - 1, col), (row - 1, col + 1),
        (row,     col - 1),                  (row,     col + 1),
        (row + 1, col - 1), (row + 1, col), (row + 1, col + 1),
    ]


def next_generation(grid):
    neighbor_counts = {}
    for (row, col) in grid:
        for nb in get_neighbors(row, col):
            neighbor_counts[nb] = neighbor_counts.get(nb, 0) + 1

    next_grid = set()
    for cell, count in neighbor_counts.items():
        if cell in grid:
            if count in (2, 3):
                next_grid.add(cell)
        else:
            if count == 3:
                next_grid.add(cell)
    return next_grid


def random_grid(density=0.25):
    return {
        (row, col)
        for row in range(ROWS)
        for col in range(COLS)
        if random.random() < density
    }


# ── Rendering helpers ────────────────────────────────────

def draw_hud_panel(screen, x, y, w, h):
    """Draw a semi-transparent dark rounded panel."""
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 170))
    pygame.draw.rect(panel, (60, 60, 60, 200), panel.get_rect(), width=1, border_radius=6)
    screen.blit(panel, (x, y))


def draw_hint_bar(screen, font, show_grid):
    """Draw the bottom hint bar with a dark background strip."""
    bar = pygame.Surface((WIDTH, 22), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 140))
    screen.blit(bar, (0, HEIGHT - 22))

    grid_hint = "G: hide grid" if show_grid else "G: show grid"
    hint = f"SPACE: pause/resume   N: step   LClick: draw   R: random   C: clear   ↑↓: speed   {grid_hint}"
    screen.blit(font.render(hint, True, COLOR_DIM), (8, HEIGHT - 18))


def draw_hover(screen, hover_cell):
    """Highlight the cell under the mouse cursor."""
    if hover_cell is None:
        return
    row, col = hover_cell
    if not (0 <= row < ROWS and 0 <= col < COLS):
        return
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    surf.fill(COLOR_HOVER)
    screen.blit(surf, (col * CELL_SIZE, row * CELL_SIZE))


# ── Main draw ────────────────────────────────────────────

def draw(screen, grid, generation, fps, running, show_grid, hover_cell, font):
    screen.fill(COLOR_BG)

    # Alive cells
    for (row, col) in grid:
        if 0 <= row < ROWS and 0 <= col < COLS:
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, COLOR_ALIVE, rect)

    # Grid lines (toggleable)
    if show_grid:
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (0, y), (WIDTH, y))

    # Hover highlight
    draw_hover(screen, hover_cell)

    # HUD panel — top left
    draw_hud_panel(screen, 6, 6, HUD_W, HUD_H)

    status_color = COLOR_RUNNING if running else COLOR_PAUSED
    status_text  = "RUNNING" if running else "PAUSED"

    hud_lines = [
        (status_text,              status_color),
        (f"Gen : {generation}",    COLOR_HUD_TEXT),
        (f"FPS : {fps}",           COLOR_HUD_TEXT),
        (f"Pop : {len(grid)}",     COLOR_HUD_TEXT),
    ]
    for i, (text, color) in enumerate(hud_lines):
        screen.blit(font.render(text, True, color), (14, 12 + i * 18))

    # Bottom hint bar
    draw_hint_bar(screen, font, show_grid)

    # Window title — always up to date
    pygame.display.set_caption(f"Conway's Game of Life  |  Gen {generation}  |  Pop {len(grid)}")


# ── Main ────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont("monospace", 14)

    grid        = set()
    running     = False
    fps         = 10
    generation  = 0
    show_grid   = True
    hover_cell  = None

    while True:
        clock.tick(fps)

        # ── Events ──────────────────────────────────────
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                hover_cell = (my // CELL_SIZE, mx // CELL_SIZE)

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    running = not running

                elif event.key == pygame.K_n:           # step one generation
                    grid = next_generation(grid)
                    generation += 1
                    running = False

                elif event.key == pygame.K_r:
                    grid       = random_grid()
                    generation = 0
                    running    = False

                elif event.key == pygame.K_c:
                    grid       = set()
                    generation = 0
                    running    = False

                elif event.key == pygame.K_g:
                    show_grid = not show_grid

                elif event.key == pygame.K_UP:
                    fps = min(fps + FPS_STEP, FPS_MAX)

                elif event.key == pygame.K_DOWN:
                    fps = max(fps - FPS_STEP, FPS_MIN)

        # ── Mouse paint (hold to draw) ───────────────────
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            cell = (my // CELL_SIZE, mx // CELL_SIZE)
            grid.add(cell)

        if pygame.mouse.get_pressed()[2]:               # right-click erases
            mx, my = pygame.mouse.get_pos()
            cell = (my // CELL_SIZE, mx // CELL_SIZE)
            grid.discard(cell)

        # ── Simulation tick ──────────────────────────────
        if running:
            grid = next_generation(grid)
            generation += 1

        # ── Draw ─────────────────────────────────────────
        draw(screen, grid, generation, fps, running, show_grid, hover_cell, font)
        pygame.display.flip()


if __name__ == "__main__":
    main()
