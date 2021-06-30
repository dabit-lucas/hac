import keyboard
import mouse
import time

flag = False
while True:

    if keyboard.is_pressed('k'):
        flag = not flag

    if flag:
        mouse.click()

    time.sleep(0.5)