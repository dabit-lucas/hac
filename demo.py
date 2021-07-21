from hac import hac
import cv2
import time
import keyboard
import traceback
import sys
import threading
import argparse

record = False
end_record = False
t = None

def timer(record_time):
    global end_record
    time.sleep(record_time)
    end_record = True
    print("End", end_record)

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', default='test')
    parser.add_argument('-k', '--keep_data', type=str2bool, default="False")
    args = parser.parse_args()

    record_time = 30

    CENTER_POS = (481, 558)
    LIFT_POS = (414, 951)
    PUNCH_POS = (476, 951)
    TRAMPLE_POS = (543, 951)

    mouse_module = hac.add_module("mouse")
    movement_module = hac.add_module("roblox_lift_game")
    hac.set_init_module(mouse_module)

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
    mouse_module.add_transition(movement_module, ["33", "33", "33"])

    movement_module.add_key_mapping("w", "walk")
    movement_module.add_key_mapping("w", "run")
    movement_module.add_key_mapping("s", "hands_on_hips")
    movement_module.add_key_mapping("a", "point_left")
    movement_module.add_key_mapping("d", "point_right")
    movement_module.add_key_mapping("space", "jump")
    movement_module.add_key_mapping("skip", "stand")
    movement_module.add_mouse_mapping("click", "arms_lift")
    movement_module.add_mouse_mapping("click", "punch")
    movement_module.add_mouse_mapping("click", "trample")
    movement_module.add_transition(mouse_module, "lateral_raise")

    cap = cv2.VideoCapture(0)
    factor = 60
    width = 16 * factor
    height = 9 * factor
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    csv_path = "C:\\Users\\JAQQ\\YOLO\\hac\\data\\actions\\" + args.dataset + "\\data.csv"
    image_dir = "C:\\Users\\JAQQ\\YOLO\\hac\\data\\actions\\"  + args.dataset + "\\image"

    count = 0                         

    locked = True

    while cap.isOpened():

        #if keyboard.is_pressed("k"):
        #    hac.start()

        try:
            s = time.time()
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue
            
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            hac.update(image, cap.get(cv2.CAP_PROP_POS_MSEC), keep_data=args.keep_data)
            hac.execute()

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            hac.holistic_tracker.draw_landmarks(image)
            #hac.hand_tracker.draw_landmarks(image)
            #hac.pose_estimator.draw_landmarks(image)
            cv2.imshow('MediaPipe Holistic', cv2.flip(image, 1))
            cv2.moveWindow('MediaPipe Holistic', 940, 460)
            
            e = time.time()
            
            if cv2.waitKey(5) & 0xFF == 27:
                break

            if record:
                if t is None:                
                    t = threading.Thread(target=timer, daemon=True, args=(record_time,))
                    t.start()
                hac.save(csv_path, image_dir, 0)

            if end_record:
                break

            if keyboard.is_pressed("r") and not record:
                record = True
                time.sleep(3)
            
        
        except Exception as e:
            traceback.print_exc()
            break

        count += 1
    cap.release()