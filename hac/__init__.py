
import os
import pickle
import pathlib
from .controller import HAC
from .hand import HandTracker, SkeletonBasedGestureDetector
from .pose import PoseEstimator, SkeletonBasedActionDetector

model_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "models/number/model.pth")
model = pickle.load(open(model_path, 'rb'))

action_model_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "models/actions/model.pth")
action_model = pickle.load(open(action_model_path, 'rb'))

hac = HAC(HandTracker(), 
          PoseEstimator(),
          SkeletonBasedGestureDetector(model), 
          SkeletonBasedActionDetector(action_model))