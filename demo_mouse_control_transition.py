from pyhac import hac
import cv2
import time
import sys
import signal
import argparse

if __name__ == "__main__":

    # add predefined modules
    slow_mouse_module = hac.add_module("mouse_control", "slow_mouse_control")
    mouse_module = hac.add_module("mouse_control", "mouse_control")
    hac.set_init_module(mouse_module)

    # create mapping between controls and actions
    mouse_module.add_mouse_mapping("mouse_left_down", ["r_five", "r_zero"])
    mouse_module.add_mouse_mapping("mouse_left_up", "r_five")
    mouse_module.add_mouse_mapping("mouse_right_down", ["l_five", "l_zero"])
    mouse_module.add_mouse_mapping("mouse_right_up", "l_five")
    mouse_module.add_mouse_mapping("right_move_diff", ["r_five", "r_five"], sensitivity_factor=3.0)
    mouse_module.add_mouse_mapping("right_move_diff", ["r_zero", "r_zero"], sensitivity_factor=3.0)
    mouse_module.add_mouse_mapping("left_move_diff", ["l_five", "l_five"], sensitivity_factor=3.0)
    mouse_module.add_mouse_mapping("left_move_diff", ["l_zero", "l_zero"], sensitivity_factor=3.0)
    mouse_module.add_mouse_mapping("roll_up", "two_index_fingers_up")
    mouse_module.add_mouse_mapping("roll_down", "two_index_fingers_down")
    mouse_module.add_transition(slow_mouse_module, ["55"]*10) # transit to slow mode after 10 frames with left hand and right hand are both gesture five

    slow_mouse_module.add_mouse_mapping("mouse_left_down", ["r_five", "r_zero"])
    slow_mouse_module.add_mouse_mapping("mouse_left_up", "r_five")
    slow_mouse_module.add_mouse_mapping("mouse_right_down", ["l_five", "l_zero"])
    slow_mouse_module.add_mouse_mapping("mouse_right_up", "l_five")
    slow_mouse_module.add_mouse_mapping("right_move_diff", ["r_five", "r_five"], sensitivity_factor=1.0)
    slow_mouse_module.add_mouse_mapping("right_move_diff", ["r_zero", "r_zero"], sensitivity_factor=1.5)
    slow_mouse_module.add_mouse_mapping("left_move_diff", ["l_five", "l_five"], sensitivity_factor=1.0)
    slow_mouse_module.add_mouse_mapping("left_move_diff", ["l_zero", "l_zero"], sensitivity_factor=1.5)
    slow_mouse_module.add_mouse_mapping("roll_up", "two_index_fingers_up")
    slow_mouse_module.add_mouse_mapping("roll_down", "two_index_fingers_down")
    slow_mouse_module.add_transition(mouse_module, ["55"]*10) # transit to fast mode after 10 frames with left hand and right hand are both gesture five

    # opencv get images from a webcam
    if sys.platform.startswith("win"):
        cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(0)

    factor = 1080 / 1920
    ui_factor = 1
    width = int(1920//2/ui_factor)
    height = width * factor
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    count = 0
    t_start = time.time()
    while cap.isOpened():

        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        ts = time.time() - t_start
        image = cv2.GaussianBlur(image, (7, 7), 0)
        # detect actions
        hac.update(image, ts)
        # execute controls
        hac.execute()

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        hac.holistic_tracker.draw_landmarks(image)

        # flip the image only for the usage habit
        cv2.imshow('HAC demo', cv2.flip(image, 1))
        cv2.moveWindow('HAC demo', 0, 0)
        
        if cv2.waitKey(5) & 0xFF == 27:
            break

        count += 1

    cap.release()
    cv2.destroyAllWindows()