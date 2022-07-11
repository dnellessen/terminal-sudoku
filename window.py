import curses
from curses.textpad import rectangle


class Window:
    rows, cols = 0, 0
    cursor_x, cursor_y = 0, 0

    def __init__(self):
        self.board = WindowBoard()

    def main(self, win):
        curses.start_color()
        curses.use_default_colors()

        Window.rows, Window.cols = win.getmaxyx()

        win.clear()
        self.board.draw(win)

        Window.cursor_x, Window.cursor_y = self.board.cursors[0][0]
        win.move(Window.cursor_x, Window.cursor_y)

        key = 0
        brow, bcol = 0, 0

        while key != 'q':
            key = win.getkey()

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
                win.addstr(str(key))
            Window.cursor_x, Window.cursor_y = self.board.cursors[brow][bcol]
            win.move(Window.cursor_x, Window.cursor_y)
            win.refresh()

    def start(self):
        curses.initscr()
        curses.wrapper(self.main)

    
class WindowBoard:
    def __init__(self):
        self.cursors = [[() * 9] * 9 for _ in range(9)]

    def add_cursor(self, brow, bcol, x, y):
        self.cursors[brow][bcol] = (x, y)

    def draw(self, win):
        center_x = Window.cols // 2
        center_y = Window.rows // 2

        board_width = 44
        board_start_x = center_x - (board_width // 2)

        board_height = 22
        board_start_y = center_y - (board_height // 2)

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

                rectangle(win, upperleft_y, upperleft_x, lowerright_y, lowerright_x)
                self.add_cursor(numrow, numcol, upperleft_y + 1, upperleft_x + 2)

                upperleft_x += 4
                lowerright_x += 4

            upperleft_x = board_start_x
            lowerright_x = board_start_x + 4
            upperleft_y += 2
            lowerright_y += 2

        rectangle(
            win, 
            board_start_y - 1, 
            board_start_x - 2, 
            board_start_y - 1 + board_height, 
            board_start_x - 2 + board_width,
        )

    
win = Window()
win.start()
