import curses

curses.initscr()
curses.start_color()
curses.use_default_colors()

curses.init_pair(1, curses.COLOR_RED, -1)
COLOR_RED = curses.color_pair(1)

curses.init_pair(2, curses.COLOR_YELLOW, -1)
COLOR_YELLOW = curses.color_pair(2)

