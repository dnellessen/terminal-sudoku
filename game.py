from copy import deepcopy
import random

from pprint import pprint


class Sudoku:
    def __init__(self):
        self.base = 3
        self.side = self.base ** 2
        self.base_range = range(self.base)

        self.board = []
        self.solution = []

        self.difficulties = {
            'easy': list(range(21, 30)),
            'medium': list(range(31, 40)),
            'hard': list(range(41, 50)),
        }
    

    def generate(self, difficulty='medium') -> list:
        self._fill_board()
        self.solve()
        self.solution = deepcopy(self.board)
        self._remove_vals(difficulty)

        return self.board

    def _fill_board(self):
        # random fill first row
        self.board = [[0]*9 for _ in range(8)]

        row = list(range(1, 10))
        random.shuffle(row)
        self.board.insert(0, row)

        # random fill first column and handle sudoku rule
        col = list(range(1, 10))
        random.shuffle(col)

        val = self.board[0][0]
        col.remove(val)
        for i in range(1, 3):
            val = self.board[0][i]
            col.remove(val)
            col.append(val)

        col_tail = col[3:]
        random.shuffle(col_tail)
        col[3:] = col_tail

        for r in range(1, 9):
            self.board[r][0] = col[r-1]

        # random fill first square
        for r in range(1, 3):
            for c in range(1, 3):
                for num in row:
                    if not self._possible(r, c, num):
                        continue
                    self.board[r][c] = num

    def _remove_vals(self, difficulty):
        diff_range = self.difficulties[difficulty]
        i = random.randint(0, len(diff_range)-1)
        total_to_remove = diff_range[i]
        removed = 0
        while removed < total_to_remove:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            
            if self.board[row][col] != 0:
                self.board[row][col] = 0
                removed += 1


    def solve(self):
        empty = self._find_empty()
        if not empty:
            return True
        row, col = empty

        for i in range(1, 10):
            if self._possible(row, col, i):
                self.board[row][col] = i

                if self.solve():
                    return True

                self.board[row][col] = 0

        return False

    def _possible(self, row, col, num):
        # row
        for c in range(9):
            if self.board[row][c] == num and col != c:
                return False

        # column
        for r in range(9):
            if self.board[r][col] == num and row != r:
                return False

        # square
        srow = (row // 3) * 3
        scol = (col // 3) * 3
        for r in range(srow, srow + 3):
            for c in range(scol, scol + 3):
                if self.board[r][c] == num and (r, c) != (row, col):
                    return False

        return True

    def _find_empty(self):
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    return (r, c)
        return None


if __name__ == "__main__":
    sudoku = Sudoku()
    sudoku.generate(difficulty='hard')
    pprint(sudoku.board)
    sudoku.solve()
    pprint(sudoku.board)
