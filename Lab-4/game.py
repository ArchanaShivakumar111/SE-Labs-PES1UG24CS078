from board import Board, COLS
from ai import AI


class Game:
    def __init__(self):
        self.board = Board()
        self.ai = AI()
        self.turn = "X"

    def run(self):
        try:
            self._play()
        except (KeyboardInterrupt, EOFError):
            print("\nGame quit.")

    def _play(self):
        print("Connect Four — you are X.")
        while True:
            self.board.print()
            if self.turn == "X":
                raw = input("Column (1-7), or q: ").strip().lower()
                if raw == "q":
                    print("Game quit.")
                    return
                try:
                    col = int(raw) - 1
                except ValueError:
                    print("Not a number. Enter a column from 1 to 7, or q to quit.")
                    continue
                if not 0 <= col < COLS:
                    print("Column must be between 1 and 7.")
                    continue
                if self.board.grid[0][col] != ".":
                    print("That column is full. Choose another.")
                    continue
            else:
                col = self.ai.choose_column(self.board)
                if col is None or not 0 <= col < COLS or self.board.grid[0][col] != ".":
                    print("AI could not make a legal move. Game over.")
                    return

            self.board.drop(col, self.turn)
            print(f"{self.turn} placed a disc in column {col + 1}.")

            if self.board.winner(self.turn):
                self.board.print()
                print(f"Game over: {self.turn} wins!")
                return
            if self.board.full():
                self.board.print()
                print("Game over: draw.")
                return

            self.turn = "O" if self.turn == "X" else "X"