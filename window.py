import curses
from curses.textpad import rectangle


class Window:
    rows, cols = 0, 0
    cursor_x, cursor_y = 0, 0

    def main(self, win):
        curses.start_color()
        curses.use_default_colors()

        self.rows, self.cols = win.getmaxyx()

        win.clear()

        self.draw_board(win)
        win.move(self.cursor_x, self.cursor_y)

        win.refresh()
        win.getch()

    def draw_board(self, win):
        center_x = self.cols // 2
        center_y = self.rows // 2

        board_width = 44
        board_start_x = center_x - (board_width // 2)

        board_height = 22
        board_start_y = center_y - (board_height // 2)

        upperleft_y = board_start_y
        upperleft_x = board_start_x
        lowerright_y = board_start_y + 2
        lowerright_x = board_start_x + 4
        for numrows in range(9):
            if numrows % 3 == 0 and numrows > 0:
                    upperleft_y += 1
                    lowerright_y += 1

            for numcols in range(9):
                if numcols % 3 == 0 and numcols > 0:
                    upperleft_x += 2
                    lowerright_x += 2

                rectangle(win, upperleft_y, upperleft_x, lowerright_y, lowerright_x)
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

    def start(self):
        curses.wrapper(self.main)

    
win = Window()
win.start()
