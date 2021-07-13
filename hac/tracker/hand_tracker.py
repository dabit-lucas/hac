import mediapipe as mp
import pandas as pd
from google.protobuf.json_format import MessageToDict
from ..utils.key_points import W_LIST_POSE, W2I_POSE, W_LIST_LEFT_HAND, W2I_LEFT_HAND, W_LIST_RIGHT_HAND, W2I_RIGHT_HAND

class HandTracker:
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.3,
                               min_tracking_confidence=0.3, max_num_hands=2, static_image_mode=False)
        self.mp_drawing = mp.solutions.drawing_utils
        self.result_hands = None
        self.target_columns = [key + "_x" for key in W_LIST_RIGHT_HAND] + [key + "_y" for key in W_LIST_RIGHT_HAND]
        self.target_columns += [key + "_x" for key in W_LIST_LEFT_HAND] + [key + "_y" for key in W_LIST_LEFT_HAND]

    def __call__(self, image, ts):
        """
        input:
            image: image
        output:
            output: hand_skeleton
        """

        self.results_hands = self.hands.process(image)
        keypoints_dict = self.pred_to_dict(self.results_hands, ts)
        hand_skeleton = self.dict_to_data(keypoints_dict)
        # no target column
        #try:
        #except Exception as e:
        #traceback.print_exc()
        #    return None

        return hand_skeleton

    def dict_to_data(self, keypoints_dict):
        df = pd.DataFrame(keypoints_dict, index=[0])               

        return df

    def pred_to_dict(self, results_hands, ts):
        
        cp_dict = {}
        cp_dict_list = []

        best_left_idx = -1
        best_left_score = 0.0
        best_right_idx = -1
        best_right_score = 0.0


        if results_hands and results_hands.multi_hand_landmarks:

            for idx, hand_landmarks in enumerate(results_hands.multi_handedness):
                
                classification = MessageToDict(results_hands.multi_handedness[idx].classification[0])

                if classification['score'] < 0.9:
                    continue

                if classification['label'] == "Left" and classification['score'] > best_left_score:
                    best_left_idx = idx
                    best_left_score = classification['score']

                if classification['label'] == "Right" and classification['score'] > best_right_score:
                    best_right_idx = idx
                    best_right_score = classification['score']

        if best_left_idx > -1:
            cp_dict_list.append(
                self.landmarks_to_dict(results_hands.multi_hand_landmarks[best_left_idx].landmark, W2I_LEFT_HAND, ts)
            )
        else:
            cp_dict_list.append(
                self.landmarks_to_dict_dummy(W2I_LEFT_HAND, ts)
            )
        
        if best_right_idx > -1:
            cp_dict_list.append(
                self.landmarks_to_dict(results_hands.multi_hand_landmarks[best_right_idx].landmark, W2I_RIGHT_HAND, ts)
            )
        else:
            cp_dict_list.append(
                self.landmarks_to_dict_dummy(W2I_RIGHT_HAND, ts)
            )
        
        for cp in cp_dict_list:
            cp_dict.update(cp)

        return cp_dict

    def landmarks_to_dict_dummy(self, w2i, ts):
 
        cp_dict = {}

        for w in w2i:
            cp_dict[w + "_x"] = 0.0
            cp_dict[w + "_y"] = 0.0
            cp_dict[w + "_v"] = 0.0

        cp_dict["ts"] = ts
        
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

        if self.results_hands and self.results_hands.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(self.results_hands.multi_hand_landmarks):
                self.mp_drawing.draw_landmarks(
                        image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return image