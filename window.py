import curses
from curses.textpad import rectangle

from copy import deepcopy

from exceptions import WindowToSmallError
from colors import COLOR_RED, COLOR_YELLOW
from game import Sudoku


class Window:
    """
    A class that handles game window using the curses module.

    Attributes
    ----------
    quit : bool
    rows, cols : tuple[int, int]
        Window dimensions.
    cursor_x, cursor_y : tuple[int, int]
        Window's cursor position.

    Methods
    -------
    start :
        Start window and game.
    show_cursor :
        Show or hide cursor on screen.
    """

    quit = False
    rows, cols = (0, 0)
    cursor_x, cursor_y = (0, 0)
    _min_rows, _min_cols = (25, 50)

    def __init__(self):
        self.board = WindowBoard()
        self.bar = WindowBar()

    def start(self) -> None:
        ''' Start window and game. '''
        curses.initscr()
        curses.wrapper(self._main)

    @staticmethod
    def show_cursor(show: bool) -> None:
        ''' Show or hide cursor on screen. '''
        curses.curs_set(int(show))

    def _main(self, stdscr) -> None:
        ''' Main loop. '''
        curses.start_color()
        curses.use_default_colors()

        Window.rows, Window.cols = stdscr.getmaxyx()
        self._check_size()
        self.board.update(stdscr)
        self.bar.draw(stdscr, self.board._difficulty)

        while not Window.quit:
            if stdscr.getmaxyx() != (Window.rows, Window.cols):
                Window.rows, Window.cols = stdscr.getmaxyx()
                self._check_size()

                stdscr.erase()
                self.board.update(stdscr)
                self.bar.draw(stdscr, self.board._difficulty)

            key = stdscr.getkey()
            self.board.handle_key(stdscr, key)
            self._handle_key(stdscr, key)

            stdscr.refresh()

    def _handle_key(self, stdscr: curses.window, key: str) -> None:
        '''
        Handles key press.

        With the ':' key the window enters to status bar to execute a command.

        Parameters
        ----------
        stdscr : curses.window
            The curses window to draw on it.
        key : str
            The pressed key.
        '''
        if key == ':':
            command = self.bar.input_command(stdscr)
            self._execute_command(stdscr, command)
    
    def _execute_command(self, stdscr: curses.window, command: str) -> None:
        '''
        Execute a command.

        Parameters
        ----------
        stdscr : curses.window
            The curses window to draw on it.
        commande : str
            The command to execute.

        Commands
        ---------
        q[uit]\n
        c[heck]\n
        s[olve]\n
        e[asy]\n
        m[edium]\n
        h[ard]\n
        '''

        match command:
            case 'q' | 'quit':
                Window.quit = True

            case 'c' | 'check':
                solved, errors = self.board.check(self.board.playing_board)
                if solved:
                    self.board.immutable(stdscr)
                    self.bar.draw(stdscr, f'{self.board._difficulty} COMPLETED')
                else:
                    self.board.mark_errors(stdscr, errors)
                    self.bar.draw(stdscr, f'{self.board._difficulty} FAILED')
                self._handle_key(stdscr, ':')
            case 's' | 'solve':
                self.bar._write_center(stdscr, f'SOLVING {self.board._difficulty}')
                self.board.visual_solve(stdscr)
                self.bar.draw(stdscr, f'{self.board._difficulty} COMPLETED')
                self._handle_key(stdscr, ':')

            case 'e' | 'easy':
                self.board.change_board(stdscr, 'easy')
                self.bar.draw(stdscr, self.board._difficulty)
                self.show_cursor(True)
            case 'm' | 'medium':
                self.board.change_board(stdscr, 'medium')
                self.bar.draw(stdscr, self.board._difficulty)
                self.show_cursor(True)
            case 'h' | 'hard':
                self.board.change_board(stdscr, 'hard')
                self.bar.draw(stdscr, self.board._difficulty)
                self.show_cursor(True)

            case _:
                self.bar.draw(stdscr, self.board._difficulty)

    def _check_size(self) -> None:
        ''' Raises WindowToSmallError if window size is too small. '''
        if Window.rows < Window._min_rows or Window.cols < Window._min_cols:
            raise WindowToSmallError('Window must have a minimum of 25 rows and 50 columns.')


class WindowBoard(Sudoku):
    """
    A class that inherits the Sudoku class to handle window's Sudoku board.

    Attributes
    ----------
    difficulty : str, default 'medium'
        The difficulty of the board (easy, medium, hard).

    playing_board : list[list]
        Deepcopy of the board.

    solved : bool
        True if board has successfully been completed.
    errors : tuple
        The indices of the errors.
        Only where the starting board has zeroes.

    cursors : list[list[tuple[int, int]]]
        Coordinates of board cells on the window.
    index_row, index_col : tuple[int, int]
        Keeps hold of index from board coordinates.
    cursors_user_accessible : list[list[bool]]
        List of booleans for if board cell is user-accessible.

    Methods
    -------
    update :
        Update window board.
    draw :
        Draw Sudoku board in the center of the window.
    change_board :
        Change and update the board.
    mark_errors :
        Mark errors on the board.
    immutable :
        Make board immutable.
    visual_solve :
        Visualizes Sudoku solving algorithm therefore solving the board.
    handle_key:
        Handles key press on board.
    """

    def __init__(self):
        super().__init__()

        self._difficulty = 'medium'

        super().generate(self._difficulty)
        self.playing_board = deepcopy(self.board)

        self.solved = False
        self.errors = None

        self.cursors = [[() * 9] * 9 for _ in range(9)]
        self.index_row, self.index_col = (0, 0)
        self.cursors_user_accessible = [[False * 9] * 9 for _ in range(9)]

        self._width = 44
        self._height = 22

    def update(self, stdscr: curses.window) -> None:
        ''' 
        Update window board. 

        Parameters
        ----------
        stdscr : curses.window
            The curses window to draw on it.

        Also See
        -----------
        change_board : Change and update the board.
        '''

        self.draw(stdscr)
        self._add_values(stdscr)
        self._move_cursor(stdscr)

    def draw(self, stdscr: curses.window) -> None:
        '''
        Draw Sudoku board in the center of the window.

        Using curses.textpad.rectangle to draw squares on window. The positions
        of the smaller rectangles' center are added to the cursors board variable.
        That way the cursor's position for the input is saved.

        Parameters
        ----------
        stdscr: curses.window
            The curses window to draw on it.
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

        for irow in range(9):
            if irow % 3 == 0 and irow > 0:
                    upperleft_y += 1
                    lowerright_y += 1

            for icol in range(9):
                if icol % 3 == 0 and icol > 0:
                    upperleft_x += 2
                    lowerright_x += 2

                rectangle(stdscr, upperleft_y, upperleft_x, lowerright_y, lowerright_x)
                self._add_cursor(irow, icol, upperleft_y + 1, upperleft_x + 2)

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

    def change_board(self, stdscr: curses.window, difficulty: str) -> None:
        ''' 
        Change and update the board.

        Parameters
        ----------
        stdscr : curses.window
            The curses window to draw on it.
        difficulty : str
            The new board's difficulty.

        Also See
        -----------
        update : Update window board. 
        '''

        self.difficulty = difficulty
        self.cursors_user_accessible = [[False * 9] * 9 for _ in range(9)]
        self.update(stdscr)

    def handle_key(self, stdscr: curses.window, key: str) -> None:
        ''' 
        Handles key press on board.

        If the key is numeric it will write its value on the board. Otherwise the
        arrow or WASD keys will change the cursor's position.

        Parameters
        ----------
        stdscr: curses.window
            The curses window to draw on it.
        key: str
            Pressed key.
        '''

        irow, icol = self.index_row, self.index_col

        if key.isnumeric() and self.cursors_user_accessible[irow][icol]:
            self._write_value(stdscr, irow, icol, key)
            
        if key == 'KEY_LEFT' or key == 'a':
            icol = icol - 1 if icol > 0 else 8
        elif key == 'KEY_RIGHT' or key == 'd':
            icol = icol + 1 if icol < 8 else 0
        elif key == 'KEY_UP' or key == 'w':
            irow = irow - 1 if irow > 0 else 8
        elif key == 'KEY_DOWN' or key == 's':
            irow = irow + 1 if irow < 8 else 0

        self.index_row, self.index_col = irow, icol
        self._move_cursor(stdscr)

    def mark_errors(self, stdscr: curses.window, errors: tuple) -> None:
        ''' 
        Mark errors on the board.

        Errors will blink in yellow and the board will no longer be
        editable by a user.

        Parameters
        ----------
        stdscr : curses.window
            The curses window to draw on it.
        errors : tuple[tuple[int, int]]
            A tuple width the errors' indices.
        '''

        style = curses.A_BLINK | COLOR_YELLOW

        for error in errors:
            irow, icol = self.index_row, self.index_col = error
            row, col = self.cursors[irow][icol]

            val = self.playing_board[irow][icol]
            if val == 0:
                val = '-'

            stdscr.move(row, col)
            stdscr.addstr(str(val), style | curses.A_BOLD)

        self.cursors_user_accessible = [[False * 9] * 9 for _ in range(9)]

    def immutable(self, stdscr) -> None:
        ''' 
        Make board immutable.

        After one second the board will fill in one color.

        Parameters
        ----------
        stdscr : curses.window
            The curses window to draw on it.
        '''

        self.cursors_user_accessible = [[False * 9] * 9 for _ in range(9)]
        curses.napms(1000)
        self.update(stdscr)

    def visual_solve(self, stdscr: curses.window) -> None:
        '''
        Visualizes Sudoku solving algorithm therefore solving the board.
        
        View Sudoku.solve() documentation for more information.
        '''

        self.playing_board = deepcopy(self.board)
        self.update(stdscr)

        Window.show_cursor(False)
        self._vsolve(stdscr)

        self.solved, self.errors = self.check(self.playing_board)
        if self.solved:
            self.immutable(stdscr)
        else: Window.show_cursor(True)


    def _vsolve(self, stdscr: curses.window) -> bool:
        empty = self._find_empty(self.playing_board)
        if not empty:
            return True
        irow, icol = empty

        nums = range(1, 10)
        for i in nums:
            if self._possible(irow, icol, i, self.playing_board):
                self.playing_board[irow][icol] = i

                self.update(stdscr)
                curses.napms(10)
                stdscr.refresh()

                if self._vsolve(stdscr):
                    return True

                self.playing_board[irow][icol] = 0

                self.update(stdscr)
                curses.napms(10)
                stdscr.refresh()

        return False

    def _add_values(self, stdscr: curses.window) -> None:
        ''' 
        Add board values to window.

        If the value is accessible by the user on the board it's styled red.

        Parameters
        ----------
        stdscr: curses.window
            The curses window to draw on it.
        '''

        for irow in range(9):
            for icol in range(9):
                cursor_x, cursor_y = self.cursors[irow][icol]
                style = curses.A_BOLD

                val = self.playing_board[irow][icol]

                if self.cursors_user_accessible[irow][icol] and val != 0:
                    style = COLOR_RED | curses.A_BOLD
                elif val == 0:
                    self.cursors_user_accessible[irow][icol] = True
                    val = ' '

                stdscr.addstr(cursor_x, cursor_y, str(val), style)

    def _write_value(self, stdscr: curses.window, irow, icol, val, style=COLOR_RED) -> None:
        ''' 
        Write value on board with given style (and bold).

        Parameters
        ----------
        stdscr: curses.window
            The curses window to draw on it.
        irow: int
            Index of row.
        icol: int
            Index of column.
        val: str
        style: str, default COLOR_RED
        '''

        self.index_row, self.index_col = irow, icol
        self.playing_board[irow][icol] = int(val)
        if val == '0':
            val = ' '
        stdscr.addstr(str(val), style | curses.A_BOLD)

    def _move_cursor(self, stdscr: curses.window) -> None:
        ''' 
        Move cursor to current board position.

        Parameters
        ----------
        stdscr: curses.window
            The curses window to draw on it.
        '''

        irow, icol = self.index_row, self.index_col
        Window.cursor_x, Window.cursor_y = self.cursors[irow][icol]
        stdscr.move(Window.cursor_x, Window.cursor_y)

    def _add_cursor(self, irow, icol, row, col):
        self.cursors[irow][icol] = (row, col)


    @property
    def difficulty_property(self):
        return self._difficulty

    @difficulty_property.setter
    def difficulty(self, difficulty: str):
        self._difficulty = difficulty
        super().generate(self._difficulty)
        self.playing_board = deepcopy(self.board)


class WindowBar:
    """
    A class that handles window's status bar.

    Methods
    -------
    draw :
        Draw empty status bar with centered text.
    input_command :
        Allows user to enter a command.
    """

    def draw(self, stdscr: curses.window, text: str) -> None:
        ''' 
        Draw empty status bar with centered text.

        Parameters
        ----------
        stdscr : curses.window
            The curses window to draw on it.
        text : str
            The text to write in the center of the bar.
        '''

        self._draw_empty(stdscr)
        self._write_center(stdscr, text)
        self._reset_cursor(stdscr)

    def _draw_empty(self, stdscr: curses.window) -> None:
        ''' 
        Draw the plain empty status bar.

        Parameters
        ----------
        stdscr : curses.window
            The curses window to draw on it.
        '''

        text = ' ' * (Window.cols - 2)
        stdscr.addstr(Window.rows-1, 1, text, curses.A_STANDOUT)

    def _write_center(self, stdscr: curses.window, text: str) -> None:
        ''' 
        Write text on center of the status bar.

        Parameters
        ----------
        stdscr : curses.window
            The curses window to draw on it.
        text : str
            The text to write in the center of the bar.
        '''

        col = (Window.cols // 2) - (len(text) // 2)
        stdscr.addstr(Window.rows-1, col+1, text.upper(), curses.A_STANDOUT)

    def _reset_cursor(self, stdscr: curses.window) -> None:
        ''' Reset the cursor to its original position on the board. '''
        stdscr.move(Window.cursor_x, Window.cursor_y)


    def input_command(self, stdscr: curses.window) -> str:
        ''' 
        Allows user to enter a command.

        The command can have a maximum length of 15 characters.
        Press escape key to exit the and enter/return to return command.

        Parameters
        ----------
        stdscr : curses.window
            The curses window to draw on it.

        Returns
        ----------
        command : str
            The command the user has entered.
        '''

        max_len = 15
        col = 2
        key = ':'

        stdscr.addstr(Window.rows-1, col, key, curses.A_STANDOUT)

        command = ''
        while True:
            key = stdscr.getkey()
            try:
                unicode_code = ord(key)
            except TypeError:
                continue

            if unicode_code == 27:  # ESCAPE
                break
            elif col > max_len:
                col, command = self._input_reset(stdscr, max_len)

            if key.isalnum():
                col, command = self._input_add(stdscr, command, col, key)
            elif unicode_code == 127 and col > 2:   # DELETE
                col, command = self._input_delete(stdscr, command, col)
            elif unicode_code == 10:   # RETURN / ENTER
                return command

    def _input_reset(self, stdscr: curses.window, max_len: int) -> tuple[int, str]:
        ''' 
        Reset the command input to null. 

        Parameters
        ----------
        stdscr : curses.window
            The curses window to draw on it.
        max_len : int
            The input's maximum length.

        Returns
        ----------
        column : Literal[2]
            The cursor's column position.
        command : Literal['']
            The currend command.
        '''

        col = 2
        stdscr.addstr(Window.rows-1, col, ':'+' '*(max_len), curses.A_STANDOUT)
        return col, ''

    def _input_add(self, stdscr, command: str, col: int, key: str) -> tuple[int, str]:
        '''
        Handle user pressing key appending it's value to the command.

        Parameters
        ----------
        stdscr : curses.window
            The curses window to draw on it.
        command : str
            The currend command.
        col : int
            The cursor's column position.
        key : str
            The pressed key.

        Returns
        ----------
        column : int
            The cursor's column position.
        command : str
            The currend command.
        '''

        col += 1
        command += key
        stdscr.addstr(Window.rows-1, col, key, curses.A_STANDOUT)
        return col, command

    def _input_delete(self, stdscr: curses.window, command: str, col: int) -> tuple[int, str]:
        '''
        Handle user pressing delete key. 
        
        Parameters
        ----------
        stdscr : curses.window
            The curses window to draw on it.
        command : str
            The currend command.
        col : int
            The cursor's column position.

        Returns
        ----------
        column : int
            The cursor's column position.
        command : str
            The currend command.
        '''

        command = command[:col-3]
        stdscr.addstr(Window.rows-1, col, ' ', curses.A_STANDOUT)
        return col - 1, command
