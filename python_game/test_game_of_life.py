# Tests for Conway's Game of Life
# Run with: python3 -m pytest test_game_of_life.py -v
# or:       python3 test_game_of_life.py

import unittest
import sys
import os

# Import only the pure logic functions — no pygame needed
sys.path.insert(0, os.path.dirname(__file__))

# Patch pygame before importing main so tests run headlessly
import unittest.mock as mock
sys.modules["pygame"] = mock.MagicMock()

from main import get_neighbors, next_generation, random_grid, ROWS, COLS


# ── get_neighbors ────────────────────────────────────────

class TestGetNeighbors(unittest.TestCase):

    def test_returns_eight_neighbors(self):
        self.assertEqual(len(get_neighbors(5, 5)), 8)

    def test_no_duplicates(self):
        neighbors = get_neighbors(5, 5)
        self.assertEqual(len(neighbors), len(set(neighbors)))

    def test_does_not_include_self(self):
        self.assertNotIn((5, 5), get_neighbors(5, 5))

    def test_correct_positions(self):
        result = set(get_neighbors(1, 1))
        expected = {
            (0, 0), (0, 1), (0, 2),
            (1, 0),         (1, 2),
            (2, 0), (2, 1), (2, 2),
        }
        self.assertEqual(result, expected)

    def test_works_at_origin(self):
        # Grid is infinite — negative coords are valid
        neighbors = set(get_neighbors(0, 0))
        self.assertIn((-1, -1), neighbors)
        self.assertIn((-1,  0), neighbors)
        self.assertIn(( 0, -1), neighbors)

    def test_all_neighbors_differ_by_one_step(self):
        for (r, c) in get_neighbors(10, 10):
            self.assertLessEqual(abs(r - 10), 1)
            self.assertLessEqual(abs(c - 10), 1)


# ── next_generation — rule coverage ──────────────────────

class TestNextGenerationRules(unittest.TestCase):

    # Rule 1: underpopulation
    def test_single_cell_dies(self):
        """A lone cell has 0 neighbors → dies."""
        self.assertEqual(next_generation({(0, 0)}), set())

    def test_two_cells_both_die(self):
        """Each cell has only 1 neighbor → both die."""
        self.assertEqual(next_generation({(0, 0), (0, 1)}), set())

    # Rule 2: survival
    def test_cell_survives_with_two_neighbors(self):
        # (1,1) has exactly 2 neighbors: (0,0) and (0,1)
        grid = {(0, 0), (0, 1), (1, 1)}
        self.assertIn((1, 1), next_generation(grid))

    def test_cell_survives_with_three_neighbors(self):
        # Centre of a 2x2 block has 3 neighbors
        grid = {(0, 0), (0, 1), (1, 0), (1, 1)}
        nxt  = next_generation(grid)
        self.assertIn((0, 0), nxt)
        self.assertIn((0, 1), nxt)
        self.assertIn((1, 0), nxt)
        self.assertIn((1, 1), nxt)

    # Rule 3: overpopulation
    def test_cell_dies_with_four_neighbors(self):
        # (1,1) surrounded by 4 alive cells
        grid = {(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)}
        self.assertNotIn((1, 1), next_generation(grid))

    def test_cell_dies_with_five_neighbors(self):
        grid = {(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)}
        self.assertNotIn((1, 1), next_generation(grid))

    # Rule 4: reproduction
    def test_dead_cell_born_with_three_neighbors(self):
        # Three cells around (1,1) — it should be born
        grid = {(0, 0), (0, 1), (0, 2)}
        self.assertIn((1, 1), next_generation(grid))

    def test_dead_cell_not_born_with_two_neighbors(self):
        grid = {(0, 0), (0, 1)}
        # No dead cell has exactly 3 alive neighbors here
        nxt = next_generation(grid)
        self.assertEqual(nxt, set())

    def test_dead_cell_not_born_with_four_neighbors(self):
        # (1,1) is dead and has 4 alive neighbors → stays dead
        grid = {(0, 0), (0, 1), (0, 2), (1, 0)}
        # (1,1) has neighbors: (0,0),(0,1),(0,2),(1,0) = 4 → not born
        self.assertNotIn((1, 1), next_generation(grid))


# ── next_generation — edge cases ─────────────────────────

class TestNextGenerationEdgeCases(unittest.TestCase):

    def test_empty_grid_stays_empty(self):
        self.assertEqual(next_generation(set()), set())

    def test_returns_a_set(self):
        self.assertIsInstance(next_generation({(0, 0)}), set)

    def test_input_grid_not_mutated(self):
        grid = {(0, 0), (0, 1), (0, 2)}
        original = grid.copy()
        next_generation(grid)
        self.assertEqual(grid, original)

    def test_works_with_negative_coordinates(self):
        # Grid is logically infinite — negative coords must work
        grid = {(-1, 0), (0, 0), (1, 0)}   # vertical blinker around origin
        nxt  = next_generation(grid)
        self.assertEqual(nxt, {(0, -1), (0, 0), (0, 1)})


# ── next_generation — known patterns ─────────────────────

class TestKnownPatterns(unittest.TestCase):

    # Still lifes — must not change
    def test_block_is_still_life(self):
        block = {(0, 0), (0, 1), (1, 0), (1, 1)}
        self.assertEqual(next_generation(block), block)

    def test_beehive_is_still_life(self):
        beehive = {(0, 1), (0, 2), (1, 0), (1, 3), (2, 1), (2, 2)}
        self.assertEqual(next_generation(beehive), beehive)

    # Oscillators
    def test_blinker_period_2(self):
        h = {(1, 0), (1, 1), (1, 2)}   # horizontal
        v = {(0, 1), (1, 1), (2, 1)}   # vertical
        self.assertEqual(next_generation(h), v)
        self.assertEqual(next_generation(v), h)

    def test_toad_period_2(self):
        gen1 = {(1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2)}
        gen2 = next_generation(gen1)
        self.assertEqual(next_generation(gen2), gen1)

    # Glider — moves diagonally, period 4
    def test_glider_period_4(self):
        gen0 = {(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)}
        gen4 = gen0
        grid = gen0
        for _ in range(4):
            grid = next_generation(grid)
        # After 4 steps the glider shifts by (+1, +1)
        shifted = {(r + 1, c + 1) for (r, c) in gen4}
        self.assertEqual(grid, shifted)

    def test_large_still_life_does_not_change(self):
        # Boat (5-cell still life)
        boat = {(0, 0), (0, 1), (1, 0), (1, 2), (2, 1)}
        self.assertEqual(next_generation(boat), boat)


# ── random_grid ──────────────────────────────────────────

class TestRandomGrid(unittest.TestCase):

    def test_returns_a_set(self):
        self.assertIsInstance(random_grid(), set)

    def test_all_cells_within_bounds(self):
        grid = random_grid()
        for (row, col) in grid:
            self.assertGreaterEqual(row, 0)
            self.assertLess(row, ROWS)
            self.assertGreaterEqual(col, 0)
            self.assertLess(col, COLS)

    def test_density_zero_gives_empty_grid(self):
        self.assertEqual(random_grid(density=0.0), set())

    def test_density_one_gives_full_grid(self):
        grid = random_grid(density=1.0)
        self.assertEqual(len(grid), ROWS * COLS)

    def test_density_is_roughly_respected(self):
        # With density=0.5 over 4800 cells, expect between 35%–65%
        grid = random_grid(density=0.5)
        ratio = len(grid) / (ROWS * COLS)
        self.assertGreater(ratio, 0.35)
        self.assertLess(ratio, 0.65)

    def test_different_calls_give_different_grids(self):
        # Statistically near-impossible to collide twice
        self.assertNotEqual(random_grid(), random_grid())


# ────────────────────────────────────────────────────────
if __name__ == "__main__":
    unittest.main(verbosity=2)
