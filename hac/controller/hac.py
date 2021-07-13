import threading
import time
import mouse
import keyboard
import pandas as pd
import pathlib
import re
import os
import numpy as np
import csv
import traceback
from collections import defaultdict, deque
from PIL import Image
from ..module import Module, KeyControl
from ..detector import RobloxLiftGameActionDetector, MouseControlGestureDetector

class HAC:

    hand_skeleton = None
    t = None    # thread
    stop = False
    last_pred_t = None
    saving_images = []
    images = deque()
    tss = deque()
    gestures = deque()
    poses = deque()
    controls = deque()
    movement_mouse = defaultdict(list)
    movement_key = defaultdict(list)
    modules = {}
    module = None

    def __init__(self, hand_tracker, pose_tracker, holistic_tracker):
        self.hand_tracker = hand_tracker
        self.pose_tracker = pose_tracker
        self.holistic_tracker = holistic_tracker

    def keep_data(self, df_data):
        self.df_data = df_data

    def update(self, image, ts, keep_data=False):
        
        if self.tss and self.tss[-1] == ts:
            return

        gesture = None
        pose = None
        control = None

        if self.holistic_tracker is None:
            hand_data = self.hand_tracker(image, ts)
            pose_data = self.pose_tracker(image, ts)
            skeleton = pd.concat([hand_data[self.hand_tracker.target_columns], pose_data[self.pose_estimator.target_columns]], axis=1)
        else:
            skeleton = self.holistic_tracker(image, ts)
        
        if not keep_data:
            control = self.module(skeleton)

        if keep_data:
            self.keep_data(skeleton)

        self.images.append(image)
        self.tss.append(ts)
        self.controls.append(control)
        
        if len(self.images) > 30:
            self.images.popleft()

        if len(self.tss) > 30:
            self.tss.popleft()

        if len(self.controls) > 30:
            self.controls.popleft()

    def add_module(self, module_name):

        if module_name == "mouse":
            detector = MouseControlGestureDetector()
        if module_name == "roblox_lift_game":
            detector = RobloxLiftGameActionDetector()

        module = Module(detector)
        self.modules[module_name] = module

        return module
        
    def set_init_module(self, module):
        self.module = module

    def execute(self):
        if len(self.controls) == 0:
            return 
        
        if not self.controls[-1]:
            return

        if isinstance(self.controls[-1], Module):
            
            for action, control in self.module.mapping.items():
                if not isinstance(self.controls[-1], KeyControl):
                    if isinstance(control, KeyControl):
                        control.release()
                else:
                    if isinstance(control, KeyControl) and control.key != self.controls[-1].key:
                        control.release()

            self.module = self.controls[-1]
        else:
            for action, control in self.module.mapping.items():
                if not isinstance(self.controls[-1], KeyControl):
                    if isinstance(control, KeyControl):
                        control.release()
                else:
                    if isinstance(control, KeyControl) and control.key != self.controls[-1].key:
                        control.release()

            if self.controls[-1].execute:
                self.controls[-1].execute()
        
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
        
        self.saving_images.append((image, image_path))
        #image_pil.save(image_path)

    def save_images(self):
        for image, path in self.saving_images:
            image_pil = Image.fromarray(image)
            image_pil.save(path)

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
    