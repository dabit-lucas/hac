import mediapipe as mp
import pandas as pd
from google.protobuf.json_format import MessageToDict

class PoseEstimator:
    
    W_LIST_POSE = [
        "n", 
        "lei", 
        "le", 
        "leo", 
        "rei",
        "re",
        "reo",
        "lea",
        "rea",
        "ml",
        "mr",
        "ls",
        "rs",
        "lel",
        "rel",
        "lw",
        "rw",
        "lp",
        "rp",
        "li",
        "ri",
        "lt",
        "rt",
        "lh",
        "rh",
        "lk",
        "rk",
        "la",
        "ra",
        "lhe",
        "rhe",
        "lf",
        "rf"
    ]

    W2I_POSE = {v: k for k, v in enumerate(W_LIST_POSE)}

    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5,
                                      min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        self.results_pose = None
        self.target_columns = [key + "_x" for key in self.W_LIST_POSE] + [key + "_y" for key in self.W_LIST_POSE]
    
    def __call__(self, image, ts):
        """
        input:
            image: image
        output:
            output: pose_skeleton
        """

        self.results_pose = self.pose.process(image)
        keypoints_dict = self.pred_to_dict(self.results_pose, ts)

        # no target column
        try:
            pose_skeleton = self.dict_to_data(keypoints_dict)
        except Exception as e:
            #traceback.print_exc()
            return None

        return pose_skeleton

    def dict_to_data(self, keypoints_dict):
        df = pd.DataFrame(keypoints_dict, index=[0])
        
                        

        return df

    def pred_to_dict(self, results_pose, ts):
        
        cp_dict = {}
        cp_dict_list = []
        
        if results_pose and results_pose.pose_landmarks:
            
            cp_dict_list.append(
                self.landmarks_to_dict(results_pose.pose_landmarks.landmark, self.W2I_POSE, ts)
            )

        for cp in cp_dict_list:
            cp_dict.update(cp)

        return cp_dict

    def landmarks_to_dict(self, landmarks, w2i, ts):

        cp_dict = {}

        for w in w2i:
            cp_dict[w + "_x"] = landmarks[w2i[w]].x
            cp_dict[w + "_y"] = -landmarks[w2i[w]].y + 1
            cp_dict[w + "_v"] = landmarks[w2i[w]].visibility

        cp_dict["ts"] = ts
        
        return cp_dict

    def draw_landmarks(self, image):

        if self.results_pose and self.results_pose.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                    image, self.results_pose.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

        return image