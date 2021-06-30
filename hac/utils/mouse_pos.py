import mouse
import win32api

while True:
    print(mouse.get_position())
    print(win32api.GetCursorPos())