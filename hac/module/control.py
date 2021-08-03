import pydirectinput
import pyautogui
import mouse
import threading
import time
import keyboard

pyautogui.FAILSAFE = False
pydirectinput.PAUSE = 0
pyautogui.PAUSE = 0

class MouseControl:

    freeze = False

    def __init__(self, method, **params):
        self.execute = getattr(self, method)
        self.method_name = method

        for key in params:
            setattr(self, key, params[key])
    
    def _check_freeze(func):
        def wrap(self, **params):
            sec = 0.01
            if not self.freeze:
                self.freeze = True
                func(self, **params)
                t = threading.Thread(target=self.freeze_timer, daemon=True, args=(sec,))
                t.start()

        return wrap

    @_check_freeze
    def click(self):
        mouse.click()

    @_check_freeze
    def mouse_left_down(self):
        mouse.press()

    @_check_freeze
    def mouse_left_up(self):
        mouse.release()

    @_check_freeze
    def mouse_right_down(self):
        mouse.press(button="right")

    @_check_freeze
    def mouse_right_up(self):
        mouse.release(button="right")

    @_check_freeze
    def right_click(self):
        mouse.right_click()

    @_check_freeze
    def roll_up(self):
        pyautogui.scroll(30) 
        print("roll_up")

    @_check_freeze
    def roll_down(self):
        pyautogui.scroll(-30) 
        print("roll_down")

    @_check_freeze
    def move_diff(self, factor=2000):
        print("move_diff")
        x1 = self.df_data_1_x.values.mean()
        x2 = self.df_data_2_x.values.mean()
        y1 = self.df_data_1_y.values.mean()
        y2 = self.df_data_2_y.values.mean()
        dx = -(x2 - x1).item() * factor
        dy = -(y2 - y1).item() * factor
        pydirectinput.move(int(dx), int(dy))
    
    def right_move_diff(self):
        self.move_diff()

    def left_move_diff(self):
        self.move_diff()

    def set_params(self, **params):
        for key in params:
            setattr(self, key, params[key]) 

    def freeze_timer(self, sec):
        time.sleep(sec)
        self.freeze = False

class KeyControl:
    def __init__(self, key, **params):
        self.key = key
        self.method_name = key

    def execute(self):

        if self.key == "skip":
            return

        if self.key == "left":
            pydirectinput.keyDown('left')
        elif self.key == "right":
            pydirectinput.keyDown('right')
        elif self.key == "skip":
            pass
        else:
            keyboard.press(self.key)

    def release(self):

        if self.key == "skip":
            return

        keyboard.release(self.key)

