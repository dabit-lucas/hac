import mouse
import threading
import time
import keyboard
import sys
import pyautogui

if sys.platform.startswith("win"):
    import pydirectinput
    pydirectinput.PAUSE = 0
    pydirectinput.FAILSAFE = False
else:
    pyautogui.PAUSE = 0

class MouseControl:

    freeze = False
    def __init__(self, method, **params):
        self.execute = getattr(self, method)
        self.method_name = method
        self.sensitivity_factor = 4.0

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
        if sys.platform.startswith("win"):
            mouse.click()
        else:
            pyautogui.click()
    @_check_freeze
    def mouse_left_down(self):
        if sys.platform.startswith("win"):
            mouse.press()
        else:
            pyautogui.mouseDown()
    @_check_freeze
    def mouse_left_up(self):
        if sys.platform.startswith("win"):
            mouse.release()
        else:
            pyautogui.mouseUp()
    @_check_freeze
    def mouse_right_down(self):
        if sys.platform.startswith("win"):
            mouse.press(button="right")
        else:
            pyautogui.mouseDown(button="right")
    @_check_freeze
    def mouse_right_up(self):
        if sys.platform.startswith("win"):
            mouse.release(button="right")
        else:
            pyautogui.mouseUp(button="right")
    @_check_freeze
    def right_click(self):
        if sys.platform.startswith("win"):
            mouse.right_click()
        else:
            mouse.right_click()
    @_check_freeze
    def roll_up(self):
        print("roll_up")
        if sys.platform.startswith("win"):
            mouse.wheel(30) 
        else:
            pyautogui.scroll(30) 
    @_check_freeze
    def roll_down(self):
        print("roll_down")
        if sys.platform.startswith("win"):
            mouse.wheel(-30)
        else:
            pyautogui.scroll(-30)
    @_check_freeze
    def move_diff(self):
        print("move_diff")
        fix_factor = 1000.0
        x1 = self.df_data_1_x.values.mean()
        x2 = self.df_data_2_x.values.mean()
        y1 = self.df_data_1_y.values.mean()
        y2 = self.df_data_2_y.values.mean()
        dx = -(x2 - x1).item() * self._sensitivity_factor * fix_factor
        dy = -(y2 - y1).item() * self._sensitivity_factor * fix_factor
        print(self._sensitivity_factor)
        if sys.platform.startswith("win"):
            pydirectinput.move(int(dx), int(dy))
        else:
            mouse.move(int(dx), int(dy), absolute=False)

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

    def release(self):
        self.mouse_left_up()
        self.mouse_right_up()

    @property
    def sensitivity_factor(self):
        return self._sensitivity_factor

    @sensitivity_factor.setter
    def sensitivity_factor(self, sensitivity_factor):
        self._sensitivity_factor = sensitivity_factor

class KeyControl:
    def __init__(self, key, **params):
        self.key = key
        self.method_name = key

    def execute(self):

        if sys.platform.startswith("win"):
            if self.key == "left":
                pydirectinput.keyDown('left')
            elif self.key == "right":
                pydirectinput.keyDown('right')
            else:
                keyboard.press(self.key)
        else:
            pyautogui.keyDown(self.key)
    def release(self):

        if sys.platform.startswith("win"):
            keyboard.release(self.key)
        else:
            pyautogui.keyUp(self.key)

