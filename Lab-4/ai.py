import random

from board import COLS


class AI:
    def choose_column(self, board, me="O", opponent="X"):
        legal = [c for c in range(COLS) if board.grid[0][c] == "."]
        if not legal:
            return None

        # 1) Win immediately if possible.
        for c in legal:
            if self._wins(board, c, me):
                return c

        # 2) Otherwise block the opponent's immediate win.
        for c in legal:
            if self._wins(board, c, opponent):
                return c

        # 3) Otherwise prefer the centre-most legal column(s).
        centre = (COLS - 1) / 2
        best = min(abs(c - centre) for c in legal)
        return random.choice([c for c in legal if abs(c - centre) == best])

    def _wins(self, board, col, token):
        """Would dropping `token` in `col` win? Leaves the board unchanged."""
        row = board.drop(col, token)
        if row is None:
            return False
        try:
            return board.winner(token)
        finally:
            board.grid[row][col] = "."  # undo the trial move