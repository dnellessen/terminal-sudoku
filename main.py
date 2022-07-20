from window import Window
from exceptions import WindowTooSmallError

import sys


difficulty = 'medium'
for arg in sys.argv:
    if arg.startswith('-'):
        match arg:
            case '-e' | '-easy':
                difficulty = 'easy'
            case '-m' | '-medium':
                difficulty = 'medium'
            case '-h' | '-hard':
                difficulty = 'hard'


win = Window()
win.board.difficulty = difficulty

try:
    win.start()
except WindowTooSmallError as error:
    print(error)
except Exception:
    print('An error occurred.')

