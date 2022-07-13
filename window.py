import curses
from curses.textpad import rectangle

from exceptions import *


class Window:
    """
    A class that handles game window using the curses module.

    Attributes
    ----------
    rows, cols : tuple[int, int]
        Window dimensions.

    Methods
    -------
    start():
        Start window and game.
    """

    rows, cols = (0, 0)
    _min_rows, _min_cols = 25, 50
    _cursor_x, _cursor_y = 0, 0

    def __init__(self):
        self.board = WindowBoard()

    def start(self):
        ''' Start window and game. '''
        curses.initscr()
        curses.wrapper(self._main)

    def _main(self, stdscr):
        curses.start_color()
        curses.use_default_colors()

        Window.rows, Window.cols = stdscr.getmaxyx()
        self._check_size()

        stdscr.clear()
        self.board.draw(stdscr)

        Window._cursor_x, Window._cursor_y = self.board.cursors[0][0]
        stdscr.move(Window._cursor_x, Window._cursor_y)

        key = 0
        brow, bcol = 0, 0

        while key != 'q':
            if stdscr.getmaxyx() != (Window.rows, Window.cols):
                Window.rows, Window.cols = stdscr.getmaxyx()
                self._check_size()

                stdscr.clear()
                self.board.draw(stdscr)
                Window._cursor_x, Window._cursor_y = self.board.cursors[brow][bcol]
                stdscr.move(Window._cursor_x, Window._cursor_y)

            key = stdscr.getkey()

            if key == 'KEY_LEFT':
                bcol -= 1
            elif key == 'KEY_RIGHT':
                bcol += 1
            elif key == 'KEY_UP':
                brow -= 1
            elif key == 'KEY_DOWN':
                brow += 1

            if bcol < 0:
                bcol = 9-1
            elif bcol > 9-1:
                bcol = 0

            if brow < 0:
                brow = 9-1
            elif brow > 9-1:
                brow = 0

            if key.isnumeric():
                if key == '0':
                    key = ' '
                stdscr.addstr(str(key))

            Window._cursor_x, Window._cursor_y = self.board.cursors[brow][bcol]
            stdscr.move(Window._cursor_x, Window._cursor_y)
            stdscr.refresh()

    def _check_size(self):
        ''' Raises WindowToSmallError if window size is too small. '''
        if Window.rows < Window._min_rows or Window.cols < Window._min_cols:
            raise WindowToSmallError('Window must have a minimum of 25 rows and 50 columns.')


    
class WindowBoard:
    """
    A class that handles window's Sudoku board.

    Attributes
    ----------
    cursors : list[list[tuple]]
        Coordinates of board cells on the window.

    Methods
    -------
    draw(stdscr):
        Draw Sudoku board in the center of the window.
    """

    def __init__(self):
        self.cursors = [[() * 9] * 9 for _ in range(9)]
        self._width = 44
        self._height = 22

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
        '''

        # added number is finetuning
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

    def _add_cursor(self, brow, bcol, x, y):
        self.cursors[brow][bcol] = (x, y)


if __name__ == "__main__":
    win = Window()
    win.start()
