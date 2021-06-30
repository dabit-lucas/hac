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

    record_time = 10

    CENTER_POS = (481, 558)
    LIFT_POS = (414, 951)
    PUNCH_POS = (476, 951)
    TRAMPLE_POS = (543, 951)

    hac.set_click("lift")
    hac.set_click("punch")
    hac.set_click("trample")
    
    hac.set_press_and_release("jump", "space")
    hac.set_press("four", "w")
    hac.set_press("five", "s")

    hac.set_move_to("zero", CENTER_POS)
    hac.set_move_to_and_click("one", LIFT_POS)
    hac.set_move_to_and_click("two", PUNCH_POS)
    hac.set_move_to_and_click("three", TRAMPLE_POS)

    if not args.keep_data:
        hac.start()
    
    cap = cv2.VideoCapture(0)
    factor = 40
    width = 16 * factor
    height = 9 * factor
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    csv_path = "C:\\Users\\JAQQ\\Desktop\\HAC\\HAC\\data\\actions\\" + args.dataset + "\\data.csv"
    image_dir = "C:\\Users\\JAQQ\\Desktop\\HAC\\HAC\\data\\actions\\"  + args.dataset + "\\image"

    count = 0                                                                                                                                 
    while cap.isOpened():
        try:
            s = time.time()
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue
            
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            hac.update(image, cap.get(cv2.CAP_PROP_POS_MSEC), keep_data=args.keep_data)
            hac.hand_tracker.draw_landmarks(image)
            hac.pose_estimator.draw_landmarks(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            cv2.imshow('MediaPipe Holistic', image)

            e = time.time()
            #print("FPS:", 1/(e-s))

            if cv2.waitKey(5) & 0xFF == 27:
                break

            if keyboard.is_pressed("k"):
                hac.save(csv_path, image_dir)
            
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