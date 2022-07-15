import curses
from curses.textpad import rectangle

from copy import deepcopy

from exceptions import *
from colors import *
from game import Sudoku


class Window:
    """
    A class that handles game window using the curses module.

    Attributes
    ----------
    rows, cols : tuple[int, int]
        Window dimensions.
    cursor_x, cursor_y : tuple[int, int]
        Window's cursor position.

    Methods
    -------
    start():
        Start window and game.
    """

    rows, cols = (0, 0)
    cursor_x, cursor_y = (0, 0)
    _min_rows, _min_cols = (25, 50)

    def __init__(self):
        self.board = WindowBoard()

    def start(self):
        ''' Start window and game. '''
        curses.initscr()
        curses.wrapper(self._main)

    def _main(self, stdscr):
        ''' Main loop. '''
        curses.start_color()
        curses.use_default_colors()

        Window.rows, Window.cols = stdscr.getmaxyx()
        self._check_size()
        self.board.update(stdscr)

        key = 0
        while key != 'q':
            if stdscr.getmaxyx() != (Window.rows, Window.cols):
                Window.rows, Window.cols = stdscr.getmaxyx()
                self._check_size()
                self.board.update(stdscr)

            key = stdscr.getkey()
            self.board.handle_key(stdscr, key)
            self.board.move_cursor(stdscr)

            stdscr.refresh()

    def _check_size(self):
        ''' Raises WindowToSmallError if window size is too small. '''
        if Window.rows < Window._min_rows or Window.cols < Window._min_cols:
            raise WindowToSmallError('Window must have a minimum of 25 rows and 50 columns.')


    
class WindowBoard(Sudoku):
    """
    A class that inherits the Sudoku class to handle window's Sudoku board.

    Attributes
    ----------
    playing_board : list[list]
        Deepcopy of the board.

    cursors : list[list[tuple[int, int]]]
        Coordinates of board cells on the window.
    index_row, index_col : tuple[int, int]
        Keeps hold of index from board coordinates.
    cursors_user_accessible : list[list[bool]]
        List of booleans for if board cell is user-accessible.

    Methods
    -------
    update(stdscr):
        Update window board.
    draw(stdscr):
        Draw Sudoku board in the center of the window.
    add_values(stdscr):
        Draw Sudoku board in the center of the window.
    write_value(stdscr, row, col, key):
        Draw Sudoku board in the center of the window.
    handle_key(stdscr, key):
        Draw Sudoku board in the center of the window.
    move_cursor(stdscr):
        Draw Sudoku board in the center of the window.
    """

    def __init__(self):
        super().__init__()
        super().generate('medium')
        self.playing_board = deepcopy(self.board)

        self.cursors = [[() * 9] * 9 for _ in range(9)]
        self.index_row, self.index_col = (0, 0)
        self.cursors_user_accessible = [[False * 9] * 9 for _ in range(9)]

        self._width = 44
        self._height = 22

    def update(self, stdscr):
        ''' 
        Update window board. 

        Parameters
        ----------
        stdscr: _curses.window
            The curses window to draw on it.
        '''

        stdscr.erase()
        self.draw(stdscr)
        self.add_values(stdscr)
        self.move_cursor(stdscr)

    def draw(self, stdscr):
        '''
        Draw Sudoku board in the center of the window.

        Using curses.textpad.rectangle to draw squares on window. The positions
        of the smaller rectangles' center are added to the cursors board variable.
        That way the cursor's position for the input is saved.

        Parameters
        ----------
        stdscr: _curses.window
            The curses window to draw on it.

        Also See
        --------
        add_values : Add board values to window.
        write_value : Write value on board styled red.
        '''

        # added number is fine-tuning
        center_x = Window.cols // 2 + 2
        center_y = Window.rows // 2

        board_start_x = center_x - (self._width // 2)
        board_start_y = center_y - (self._height // 2)

        upperleft_y = board_start_y
        upperleft_x = board_start_x
        lowerright_y = board_start_y + 2
        lowerright_x = board_start_x + 4

        for numrow in range(9):
            if numrow % 3 == 0 and numrow > 0:
                    upperleft_y += 1
                    lowerright_y += 1

            for numcol in range(9):
                if numcol % 3 == 0 and numcol > 0:
                    upperleft_x += 2
                    lowerright_x += 2

                rectangle(stdscr, upperleft_y, upperleft_x, lowerright_y, lowerright_x)
                self._add_cursor(numrow, numcol, upperleft_y + 1, upperleft_x + 2)

                upperleft_x += 4
                lowerright_x += 4

            upperleft_x = board_start_x
            lowerright_x = board_start_x + 4
            upperleft_y += 2
            lowerright_y += 2

        rectangle(
            stdscr, 
            board_start_y - 1, 
            board_start_x - 2, 
            board_start_y - 1 + self._height, 
            board_start_x - 2 + self._width,
        )

    def add_values(self, stdscr):
        ''' 
        Add board values to window.

        If the value is accessible by the user on the board it's styled
        in red. If it's a fixed value it's bolded.

        Parameters
        ----------
        stdscr: _curses.window
            The curses window to draw on it.

        Also See
        --------
        write_value : Write value on board styled red.
        '''

        for r in range(9):
            for c in range(9):
                cursor_x, cursor_y = self.cursors[r][c]
                style = curses.A_BOLD

                val = self.playing_board[r][c]

                if self.cursors_user_accessible[r][c] and val != 0:
                    style = COLOR_RED
                elif val == 0:
                    self.cursors_user_accessible[r][c] = True
                    val = ' '

                stdscr.addstr(cursor_x, cursor_y, str(val), style)

    def write_value(self, stdscr, row, col, key):
        ''' 
        Write value on board styled red.

        Parameters
        ----------
        stdscr: _curses.window
            The curses window to draw on it.
        row: int
        col: int
        key: str
            Pressed key.

        Also See
        --------
        add_values : Add board values to window.
        '''

        self.playing_board[row][col] = int(key)
        if key == '0':
            key = ' '
        stdscr.addstr(str(key), COLOR_RED)

    def handle_key(self, stdscr, key):
        ''' 
        Handles key press on board.

        If the key is numeric it will write its value on the board. Otherwise the
        arrow or WASD keys will change the cursor's position.

        Parameters
        ----------
        stdscr: _curses.window
            The curses window to draw on it.
        key: str
            Pressed key.

        Also See
        --------
        write_value : Write value on board styled red.
        '''

        row, col = self.index_row, self.index_col

        if key.isnumeric() and self.cursors_user_accessible[row][col]:
            self.write_value(stdscr, row, col, key)
            
        if key == 'KEY_LEFT' or key == 'a':
            col = col - 1 if col > 0 else 8
        elif key == 'KEY_RIGHT' or key == 'd':
            col = col + 1 if col < 8 else 0
        elif key == 'KEY_UP' or key == 'w':
            row = row - 1 if row > 0 else 8
        elif key == 'KEY_DOWN' or key == 's':
            row = row + 1 if row < 8 else 0

        self.index_row, self.index_col = row, col

    def move_cursor(self, stdscr):
        ''' 
        Move cursor to current board position.

        Parameters
        ----------
        stdscr: _curses.window
            The curses window to draw on it.
        '''

        row, col = self.index_row, self.index_col
        Window.cursor_x, Window.cursor_y = self.cursors[row][col]
        stdscr.move(Window.cursor_x, Window.cursor_y)

    def _add_cursor(self, irow, icol, row, col):
        self.cursors[irow][icol] = (row, col)


if __name__ == "__main__":
    win = Window()
    win.start()
