from pyhac import hac
import cv2
import time
import sys
import signal
import argparse

if __name__ == "__main__":

    # add predefined modules
    mouse_module = hac.add_module("gather_town")
    hac.set_init_module(mouse_module)

    # create mapping between controls and actions
    mouse_module.add_key_mapping("left", "r_point_left")
    mouse_module.add_key_mapping("right", "r_point_right")
    mouse_module.add_key_mapping("up", "r_point_up")
    mouse_module.add_key_mapping("down", "r_point_down")
    mouse_module.add_key_mapping("1", ["wave_hand"] * 3)
    mouse_module.add_key_mapping("2", ["love"] * 3)
    mouse_module.add_key_mapping("4", ["thumb_up"] * 3)
    mouse_module.add_key_mapping("5", ["question_mark"] * 3)
    
    # opencv get images from a webcam
    if sys.platform.startswith("win"):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
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