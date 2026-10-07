import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from ai import AI
from board import Board, ROWS, COLS
from game import Game


def place(board, token, cells):
    """Put token at (row, col) cells; row 0 is the top row."""
    for r, c in cells:
        board.grid[r][c] = token


def run_game(inputs, setup=None):
    """Run a Game with scripted input; return everything it printed."""
    game = Game()
    if setup:
        setup(game)
    out = io.StringIO()
    with patch("builtins.input", side_effect=inputs), redirect_stdout(out):
        game.run()
    return out.getvalue(), game


class TestWinDetection(unittest.TestCase):
    def test_horizontal(self):
        b = Board()
        place(b, "X", [(5, 0), (5, 1), (5, 2), (5, 3)])
        self.assertTrue(b.winner("X"))

    def test_vertical(self):
        b = Board()
        place(b, "X", [(2, 4), (3, 4), (4, 4), (5, 4)])
        self.assertTrue(b.winner("X"))

    def test_diagonal_up_right(self):
        b = Board()
        place(b, "X", [(5, 0), (4, 1), (3, 2), (2, 3)])
        self.assertTrue(b.winner("X"))

    def test_diagonal_up_left(self):
        b = Board()
        place(b, "X", [(5, 6), (4, 5), (3, 4), (2, 3)])
        self.assertTrue(b.winner("X"))

    def test_three_in_a_row_is_not_a_win(self):
        b = Board()
        place(b, "X", [(5, 0), (5, 1), (5, 2)])
        place(b, "X", [(2, 4), (3, 4), (4, 4)])
        place(b, "X", [(5, 6), (4, 5), (3, 4)])
        self.assertFalse(b.winner("X"))


class TestInvalidInputAndEnding(unittest.TestCase):
    def test_non_number(self):
        out, game = run_game(["abc", "q"])
        self.assertIn("Not a number", out)
        self.assertTrue(all(c == "." for row in game.board.grid for c in row))

    def test_out_of_range(self):
        out, game = run_game(["0", "8", "q"])
        self.assertEqual(out.count("Column must be between 1 and 7."), 2)
        self.assertTrue(all(c == "." for row in game.board.grid for c in row))

    def test_empty_input(self):
        out, _ = run_game(["", "q"])
        self.assertIn("Not a number", out)

    def test_full_column_rejected_without_changing_board(self):
        def setup(game):
            for r in range(ROWS):
                game.board.grid[r][0] = "X" if r % 2 == 0 else "O"
        out, game = run_game(["1", "q"], setup)
        before = [row[:] for row in game.board.grid]
        self.assertIn("That column is full", out)
        self.assertEqual(game.board.grid, before)
        self.assertNotIn("placed a disc", out)

    def test_quit(self):
        out, _ = run_game(["q"])
        self.assertIn("Game quit.", out)

    def test_end_of_input_exits_cleanly(self):
        out, _ = run_game([EOFError()])
        self.assertIn("Game quit.", out)

    def test_ctrl_c_exits_cleanly(self):
        out, _ = run_game([KeyboardInterrupt()])
        self.assertIn("Game quit.", out)

    def test_win_stops_game_before_next_turn(self):
        def setup(game):
            place(game.board, "X", [(5, 0), (5, 1), (5, 2)])
        # Only one input is supplied: if the game asked for another turn it would crash.
        out, _ = run_game(["4"], setup)
        self.assertIn("X wins", out)

    def test_draw(self):
        def setup(game):
            for r in range(ROWS):
                for c in range(COLS):
                    game.board.grid[r][c] = "X" if (c + r // 2) % 2 == 0 else "O"
            game.board.grid[0][0] = "."  # X makes the last move here
        out, game = run_game(["1"], setup)
        self.assertIn("draw", out)
        self.assertTrue(game.board.full())

    def test_feedback_once_per_move(self):
        out, _ = run_game(["4", "q"])
        self.assertEqual(out.count("placed a disc"), 2)  # one for X, one for the AI


class TestAI(unittest.TestCase):
    def test_ai_takes_immediate_win(self):
        b = Board()
        place(b, "O", [(5, 0), (5, 1), (5, 2)])
        self.assertEqual(AI().choose_column(b), 3)

    def test_ai_blocks_immediate_loss(self):
        b = Board()
        place(b, "X", [(5, 0), (5, 1), (5, 2)])
        self.assertEqual(AI().choose_column(b), 3)

    def test_ai_prefers_own_win_over_block(self):
        b = Board()
        place(b, "O", [(5, 0), (5, 1), (5, 2)])
        place(b, "X", [(5, 6), (4, 6), (3, 6)])
        self.assertEqual(AI().choose_column(b), 3)

    def test_ai_leaves_board_unchanged(self):
        b = Board()
        place(b, "X", [(5, 0), (5, 1), (5, 2)])
        before = [row[:] for row in b.grid]
        AI().choose_column(b)
        self.assertEqual(b.grid, before)

    def test_ai_never_picks_full_column(self):
        b = Board()
        for r in range(ROWS):
            b.grid[r][3] = "X" if r % 2 == 0 else "O"
        for _ in range(50):
            self.assertNotEqual(AI().choose_column(b), 3)

    def test_ai_returns_none_when_board_full(self):
        b = Board()
        for r in range(ROWS):
            for c in range(COLS):
                b.grid[r][c] = "X" if (c + r // 2) % 2 == 0 else "O"
        self.assertIsNone(AI().choose_column(b))


if __name__ == "__main__":
    unittest.main(verbosity=2)
