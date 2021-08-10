# Development guideline

## Structure of HAC
A processing pipeline is:
![processing pipeline](https://i.imgur.com/RQDraza.png)

### Tracker
A tracker can extract skeleton from an image.
The input will be an image, and the output will be a dataframe with one row of the skeleton data. Check ```hac.tracker``` for more details.

### Detector
A detector can perform the action recognition given the skeleton data.
The input will be the skeleton data, and the output will be a name of the action (e.g. "walk", "left-five"). Check ```hac.detector``` for more details.

### Mapping
A Module create mappings between actions and controls (e.g. a mapping between "walk" and press key "w"). Check ```hac.module``` for more details

### Execute
Execute controls (e.g. simulating a mouse click) from a mapping. You can trace the process from the function ```execute``` in ```hac.controller.hac```

### Human action controller
A controller can contains multiple modules, we can set a transition action to transit from one module to another (e.g. from a mouse control module to a keyboard control module), to satisify the needs of complex controls. Check ```hac.controller``` for more details.

## Models of detectors
We implement a simple action detector by taking [this paper](https://arxiv.org/abs/1801.07455) as a reference. 

### Model
We use Pytorch as the first version of action detector model. Check ```hac.model``` for more details.
The ids of key points of a body and a hand are defined by
https://google.github.io/mediapipe/solutions/hands.html and
https://google.github.io/mediapipe/solutions/pose.html

### Trained model
The trained models contain models for different purposes. For example, ```hac.trained_model.gcn.gestures``` is useful for the mouse control. ```hac.trained_model.gcn.actions``` can be used for playing game with simulated keyboard control.

## Transit among modules
There are a lot of keys on a keyboard, in the same time, we have to control the mouse, not to mention the combination of them. Even though, there are plenty of human actions, the existence of the false positive or the true nagative, urging us to select actions which are different in the feature space. This fact limit the size of an action set in one module. So we design a mechanism which allow us to transit among multiple modules with a trasition action. 
![](https://i.imgur.com/F9oBXEE.png)