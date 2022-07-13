from copy import deepcopy
import random

from pprint import pprint


class Sudoku:
    def __init__(self):
        self.board = []
        self.solution = []

        self.difficulties = {
            'easy': list(range(21, 30)),
            'medium': list(range(31, 40)),
            'hard': list(range(41, 50)),
        }
    
    
    def generate(self, difficulty='medium') -> list:
        '''
        Generate a Sudoku board.

        By randomly filling the first row, column and square of an empty board
        by respecting to Sudoku rules. Then the board get solved using a 
        backtracking algorithm. Depending on the difficulty, x numbers are removed 
        from the board (substituted with 0).

        Parameters
        ----------
        difficulty : str, default 'medium'
            The difficulty of the board (easy, medium, hard).

        Returns
        -------
        list
            The generated board.

        See Also
        --------
        solve : Solve a Sudoku board.

        Examples
        --------
        >>> sudoku.generate('hard')
        [[0, 0, 0, 4, 0, 6, 0, 0, 3],
         [5, 0, 6, 1, 2, 0, 0, 0, 9],
         [3, 8, 0, 5, 0, 9, 0, 0, 0],
         [0, 1, 3, 0, 4, 0, 6, 0, 7],
         [0, 0, 0, 0, 0, 0, 0, 1, 8],
         [9, 0, 7, 0, 0, 0, 2, 4, 5],
         [0, 9, 0, 0, 3, 0, 8, 5, 0],
         [4, 0, 0, 0, 0, 1, 7, 6, 2],
         [0, 0, 2, 0, 6, 0, 0, 0, 1]]
        '''

        self._fill_board()
        self._solve()
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


    def solve(self) -> list:
        '''
        Solve a Sudoku board.

        Using a backtracking algorithm to solve a Sudoku board.

        Returns
        -------
        list
            The solved board.

        See Also
        --------
        generate : Generate a Sudoku board.

        Examples
        --------
        >>> sudoku.solve()
        [[1, 2, 9, 4, 8, 6, 5, 7, 3],
         [5, 7, 6, 1, 2, 3, 4, 8, 9],
         [3, 8, 4, 5, 7, 9, 1, 2, 6],
         [8, 1, 3, 2, 4, 5, 6, 9, 7],
         [2, 4, 5, 6, 9, 7, 3, 1, 8],
         [9, 6, 7, 3, 1, 8, 2, 4, 5],
         [6, 9, 1, 7, 3, 2, 8, 5, 4],
         [4, 3, 8, 9, 5, 1, 7, 6, 2],
         [7, 5, 2, 8, 6, 4, 9, 3, 1]]
        '''

        self._solve()
        return self.board

    def _solve(self):
        empty = self._find_empty()
        if not empty:
            return True
        row, col = empty

        nums = list(range(1, 10))   # shuffle for random in generate
        random.shuffle(nums)        # (has no effects on algorithm)
        for i in nums:
            if self._possible(row, col, i):
                self.board[row][col] = i

                if self._solve():
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
