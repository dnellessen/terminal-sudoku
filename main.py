from window import Window
from exceptions import WindowToSmallError

win = Window()

try:
    win.start()
except WindowToSmallError as error:
    print(error)
except Exception:
    print('An error occurred.')

