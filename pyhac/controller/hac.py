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
import torch

from collections import defaultdict, deque
from PIL import Image

from ..module import Module, KeyControl
from ..detector import Detector

class HAC:

    saved_images = []    # images to data
    images = deque()     # captured images
    tss = deque()        # timestamps
    controls = deque()   # controls need to be executed
    modules = {}         # available modules of this controller
    module = None        # current module
    buffer_size = 10

    def __init__(self, holistic_tracker):
        """
        Human Action Controller (HAC)
        A Human action controller needs a holistic tracker to extract a skeleton from an image.

        inputs:
            holistic_tracker: a tracker to extract a skeleton from an image
                              take hac.tracker.holistic_tracker as a reference.
        """
        self.holistic_tracker = holistic_tracker

    def add_module(self, module_name):
        """
        Add an module to HAC.
        
        inputs: 
            module_name: a module contains a set of actions which can be detected by a detector.
        """
        model_data_path = os.path.join("pyhac\\trained_model\\gcn", \
                                        module_name, "best_model.pth")
        model_data = torch.load(model_data_path)
        detector = Detector(model_data)
        module = Module(detector)
        self.modules[module_name] = module

        return module
        
    def set_init_module(self, module):
        """
        Set a default module. Check hac.module to know more about modules
        """

        self.module = module

    def buffer_resize(self):

        if len(self.images) > self.buffer_size:
            self.images.popleft()

        if len(self.tss) > self.buffer_size:
            self.tss.popleft()

        if len(self.controls) > self.buffer_size:
            self.controls.popleft()

    def update(self, image, ts, keep_data=False):
        '''
        We call the function ```update``` every frame to capture an action from a skeleton, 
        and then generate controls.
        '''

        if self.tss and self.tss[-1] == ts:
            return

        # capture the skeleton from an image
        skeleton = self.holistic_tracker(image, ts)
        
        if keep_data:
            control = None
            self.df_data = skeleton
        else:
            # skeleton -> action detection -> control
            control = self.module(skeleton)
        
        self.images.append(image)
        self.tss.append(ts)
        self.controls.append(control)

        self.buffer_resize()

    def release_keys(self):
        """
        Release keys which aren't pressed.
        """
        for action, control in self.module.mapping.items():
            if not isinstance(self.controls[-1], KeyControl):
                if isinstance(control, KeyControl):
                    control.release()
            else:
                if isinstance(control, KeyControl) and control.key != self.controls[-1].key:
                    control.release()

    def execute(self):
        """
        Execute controls (e.g. move mouse or press keys)
        """
        if len(self.controls) == 0:
            return 
        
        if not self.controls[-1]:
            return

        self.release_keys() # release not pressed keys

        if isinstance(self.controls[-1], Module):
            self.module = self.controls[-1]
        else:
            if self.controls[-1].execute:
                self.controls[-1].execute()
        
    def save(self, csv_path, image_dir, label):
        """
        For collecting data.
        """

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
        
        self.saved_images.append((image, image_path))

    def save_images(self):
        """
        Call save_images after the end of data collection, to save all images once.
        """

        for image, path in self.saved_images:
            image_pil = Image.fromarray(image)
            image_pil.save(path)