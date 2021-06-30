import threading
import time
import mouse
import keyboard
import pandas as pd
import pathlib
import re
import os
import numpy as np
import pywinauto
import csv
from collections import defaultdict, deque
from PIL import Image

class MouseControl:

    freeze = False

    def __init__(self, method, **params):
        self.execute = getattr(self, method)
        for key in params:
            setattr(self, key, params[key])
    
    def _check_freeze(func):
        def wrap(self):
            sec = 1
            if not self.freeze:
                self.freeze = True
                func(self)
                sec = 1
                t = threading.Thread(target=self.freeze_timer, daemon=True, args=(sec,))
                t.start()

        return wrap

    @_check_freeze
    def move_to_and_click(self):

        '''
        need pos
        '''

        #mouse.move(self.pos[0], self.pos[1])
        pywinauto.mouse.move(coords=(self.pos[0], self.pos[1]))
        time.sleep(0.02)
        mouse.click()

    @_check_freeze
    def move_to(self):
        pywinauto.mouse.move(coords=(self.pos[0], self.pos[1]))
    
    @_check_freeze
    def click(self):
        mouse.click()

    @_check_freeze
    def right_click(self):
        mouse.right_click()

    def set_params(self, **params):
        for key in params:
            setattr(self, key, params[key]) 

    def freeze_timer(self, sec):
        time.sleep(sec)
        self.freeze = False
        
class KeyboardControl():
    pass

class HAC:

    hand_skeleton = None
    t = None    # thread
    stop = False
    last_pred_t = None
    images = deque()
    tss = deque()
    gestures = deque()
    poses = deque()
    movement_mouse = defaultdict(list)
    movement_key = defaultdict(list)

    def __init__(self, hand_tracker, pose_estimator, gesture_detector, action_detector):
        self.hand_tracker = hand_tracker
        self.pose_estimator = pose_estimator
        self.gesture_detector = gesture_detector
        self.action_detector = action_detector   

    def keep_data(self, df_data):
        self.df_data = df_data

    def update(self, image, ts, keep_data=False):
        
        if self.tss and self.tss[-1] == ts:
            return

        gesture = None
        hand_data = self.hand_tracker(image, ts)
        if len(hand_data.columns):
            if not keep_data:
                gesture = self.gesture_detector(hand_data)
        else:
            # keep same shape as data
            hand_data = pd.DataFrame([[None] * len(self.hand_tracker.target_columns)], columns=self.hand_tracker.target_columns)

        pose = None
        pose_data = self.pose_estimator(image, ts)
        
        if len(pose_data.columns):
            if not keep_data:
                pose = self.action_detector(pose_data)
        else:
            pose_data = pd.DataFrame([[None] * len(self.pose_estimator.target_columns)], columns=self.pose_estimator.target_columns)

            print("B", len(pose_data.columns))

        if keep_data:
            self.keep_data(pd.concat([hand_data[self.hand_tracker.target_columns], pose_data[self.pose_estimator.target_columns]], axis=1))

        self.images.append(image)
        self.tss.append(ts)
        self.gestures.append(gesture)
        self.poses.append(pose)

        if len(self.images) > 30:
            self.images.popleft()

        if len(self.tss) > 30:
            self.tss.popleft()

        if len(self.gestures) > 30:
            self.gestures.popleft()

        if len(self.poses) > 30:
            self.poses.popleft()

    def start(self):
        self.t = threading.Thread(target=self.run, daemon=True)
        self.t.start()
        
    def run(self):
        try:
            while not self.stop:
                if self.tss:
                    print('Gesture:', self.gestures[-1], 'Pose:', self.poses[-1])
                    self.last_pred_t = self.tss[-1]
                    self.execute()
                # limit fps 120, otherwise too many detection
                time.sleep(1/120)
        except Exception as e:
            print("Thread Error:", e)
            self.stop = True

    def execute(self):

        if len(self.gestures) == 0:
            return

        gesture = self.gestures[-1]
        if gesture in self.movement_mouse.keys():
            for mouse_control in self.movement_mouse[gesture]:
                mouse_control.execute()


        if gesture in self.movement_key.keys():
            for key_control in self.movement_key[gesture]:
                keyboard.press(key_control)

        for g in self.movement_key.keys():
            if gesture == g:
                continue
            keyboard.release(self.movement_key[g])

        pose = self.poses[-1]
        if pose in self.movement_mouse.keys():
            for mouse_control in self.movement_mouse[pose]:
                mouse_control.execute()

        if pose in self.movement_key.keys():
            for key_control in self.movement_key[pose]:
                keyboard.press(key_control)

    def set_click(self, movement, button='left'):
        if button == 'left':
            self.movement_mouse[movement].append(MouseControl('click'))
        elif button == 'right':
            self.movement_mouse[movement].append(MouseControl('right_click'))
        else:
            raise NotImplementedError

    def set_press_and_release(self, movement, key):
        """
        input:
            movement: type(str) "jump", "one", "two" 
        """
        self.movement_key[movement].append(key)

    def set_press(self, movement, key):
        """
        input:
            movement: type(str) "jump", "one", "two" 
        """
        self.movement_key[movement].append(key)


    def set_move_to_and_click(self, movement, pos):
        self.movement_mouse[movement].append(MouseControl('move_to_and_click', pos=pos))

    def set_move_to(self, movement, pos):
        self.movement_mouse[movement].append(MouseControl('move_to', pos=pos))

    def save(self, csv_path, image_dir, label):

        csv_dir = os.path.dirname(csv_path)
        image_name = str(int(time.time() * 1000)) + ".png"
        image_path = os.path.join(image_dir, image_name)

        pathlib.Path(csv_dir).mkdir(exist_ok=True, parents=True)
        pathlib.Path(image_dir).mkdir(exist_ok=True, parents=True)

        if label is None:
            label = input("Label: ")
            label = re.findall("\d+", label)[0]
        self.df_data["image_name"] = [image_name]
        self.df_data["label"] = [label]

        image = self.images[-1]

        if os.path.exists(csv_path):
            with open(csv_path, 'a') as f:
                write = csv.writer(f)
                write.writerow(self.df_data.values[0,:].tolist())
        else:
            df_data = self.df_data
            df_data.to_csv(csv_path, index=False)
        
        image_pil = Image.fromarray(image)
        image_pil.save(image_path)

    def list_gestures(self):
        gestures = []

        return gestures

    def list_poses(self):
        poses = []

        return poses

    def list_actions(self):
        
        actions = []

        return actions

    def list_movements(self):

        return self.list_gestures() + self.list_poses() + self.list_actions()