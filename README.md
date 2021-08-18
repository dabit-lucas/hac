# Human Action Controller (HAC)

## Goal
A human action controller running on different platforms.

| Fun      | Easy-to-use |
| -------- | --------    |
| **Accurate** | **Anywhere** |

## Fun Examples

### Mouse Control
![Mouse Control](https://raw.githubusercontent.com/dabit-lucas/hac/main/images/mouse_control.gif)

### Keyboard Control
![Keyboard Control](https://raw.githubusercontent.com/dabit-lucas/hac/main/images/down.gif)

### Playing Game
![Pikachu](https://raw.githubusercontent.com/dabit-lucas/hac/main/images/pikachu.gif)

### Enhancing interaction
![Gather Town](https://raw.githubusercontent.com/dabit-lucas/hac/main/images/gather_town.gif)

## Solutions provided by HAC
|      Platform      |      Module      | Progress | Comment |
|:------------------:|:----------------:|:--------:|:-------:|
| PC / Win10 |  Mouse Control   |    V     |         |
| PC / Win10 | Keyboard Control |    V     |         |
| PC / Ubuntu | Mouse Control |         |         |
| PC / Ubuntu | Keyboard Control |         |         |

## Getting started

### Installation
```
$ pip install pyhac
```
### Run the demo of mouse control
```
$ git clone https://github.com/dabit-lucas/hac.git
$ cd hac
$ python demo.py
```

### Recording custom actions
```
$ python recording.py -d {action name} -k True
```
Press key "r" to start recording, the data will be saved into `./data`

### Training a custom module
Here is an example of a config file of action set, 
```
{
    "actions": [
        "r_five",
        "r_zero",
        "l_five",
        "l_zero",
        "two_index_fingers_up",
        "two_index_fingers_down",
        "33",
        "55",
        "sit"
    ],
    "type": "gesture_only"
}
```
These actions form a model by running a training process:
```
$ python train.py --conf {path_of_action} --model_name {name_of_model}
```
The generated model will become a module. Take mouse control module as an exmaple, it can create mappings among actions and controls by the following code:
```
mouse_module = hac.add_module("mouse_control")
hac.set_init_module(mouse_module)

# create mapping between controls and actions
mouse_module.add_mouse_mapping("mouse_left_down", ["r_five", "r_zero"])
mouse_module.add_mouse_mapping("mouse_left_up", "r_five")
mouse_module.add_mouse_mapping("mouse_right_down", ["l_five", "l_zero"])
mouse_module.add_mouse_mapping("mouse_right_up", "l_five")
mouse_module.add_mouse_mapping("right_move_diff", ["r_five", "r_five"])
mouse_module.add_mouse_mapping("right_move_diff", ["r_zero", "r_zero"])
mouse_module.add_mouse_mapping("left_move_diff", ["l_five", "l_five"])
mouse_module.add_mouse_mapping("left_move_diff", ["l_zero", "l_zero"])
mouse_module.add_mouse_mapping("roll_up", "two_index_fingers_up")
mouse_module.add_mouse_mapping("roll_down", "two_index_fingers_down") 
```
If the `five` gesture with a right hand shows in consecutive two frames `["r_five", "r_five"]`, then do control `right_move_diff`, which means moving the mouse cursor. The above description can be represented by the following code:
```
mouse_module.add_mouse_mapping("right_move_diff", ["r_five", "r_five"])
```

## Development guideline
[The structure of HAC](https://github.com/dabit-lucas/hac/tree/main/pyhac/README.md)

## Community
Welcome to ask any question in issues.

## Contributing
Any contribution is welcomed. Please fork this repo and summit a pull request.