from window import Window
from exceptions import WindowTooSmallError

win = Window()

try:
    win.start()
except WindowTooSmallError as error:
    print(error)
except Exception:
    print('An error occurred.')

