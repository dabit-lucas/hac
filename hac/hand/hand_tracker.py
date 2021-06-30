import mediapipe as mp
import pandas as pd
from google.protobuf.json_format import MessageToDict

class HandTracker:
    
    W_LIST_LEFT_HAND = [
        "l_w",
        "l_t_c",
        "l_t_m",
        "l_t_i",
        "l_t_t",
        "l_i_m",
        "l_i_p",
        "l_i_d",
        "l_i_t",
        "l_m_m",
        "l_m_p",
        "l_m_d",
        "l_m_t",
        "l_r_m",
        "l_r_p",
        "l_r_d",
        "l_r_t",
        "l_p_m",
        "l_p_p",
        "l_p_d",
        "l_p_t",
    ]

    W2I_LEFT_HAND = {v: k for k, v in enumerate(W_LIST_LEFT_HAND)}

    W_LIST_RIGHT_HAND = [
        "r_w",
        "r_t_c",
        "r_t_m",
        "r_t_i",
        "r_t_t",
        "r_i_m",
        "r_i_p",
        "r_i_d",
        "r_i_t",
        "r_m_m",
        "r_m_p",
        "r_m_d",
        "r_m_t",
        "r_r_m",
        "r_r_p",
        "r_r_d",
        "r_r_t",
        "r_p_m",
        "r_p_p",
        "r_p_d",
        "r_p_t",
    ]

    W2I_RIGHT_HAND = {v: k for k, v in enumerate(W_LIST_RIGHT_HAND)}

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5,
                               min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        self.result_hands = None
        self.target_columns = [key + "_x" for key in self.W_LIST_RIGHT_HAND] + [key + "_y" for key in self.W_LIST_RIGHT_HAND]
        #self.target_columns += [key + "_x" for key in self.W_LIST_LEFT_HAND] + [key + "_y" for key in self.W_LIST_LEFT_HAND]

    def __call__(self, image, ts):
        """
        input:
            image: image
        output:
            output: hand_skeleton
        """

        self.results_hands = self.hands.process(image)
        keypoints_dict = self.pred_to_dict(self.results_hands, ts)

        # no target column
        try:
            hand_skeleton = self.dict_to_data(keypoints_dict)
        except Exception as e:
            #traceback.print_exc()
            return None

        return hand_skeleton

    def dict_to_data(self, keypoints_dict):
        df = pd.DataFrame(keypoints_dict, index=[0])               

        return df

    def pred_to_dict(self, results_hands, ts):
        
        cp_dict = {}
        cp_dict_list = []
        if results_hands and results_hands.multi_hand_landmarks:
            
            for idx, hand_landmarks in enumerate(results_hands.multi_hand_landmarks):
                
                classification = MessageToDict(results_hands.multi_handedness[idx].classification[0])

                if classification['score'] < 0.9:
                    continue

                if classification['label'] == "Left":
                    continue

                    cp_dict_list.append(
                        self.landmarks_to_dict(hand_landmarks.landmark, self.W2I_LEFT_HAND, ts)
                    )
                else:
                    cp_dict_list.append(
                        self.landmarks_to_dict(hand_landmarks.landmark, self.W2I_RIGHT_HAND, ts)
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

        if self.results_hands and self.results_hands.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(self.results_hands.multi_hand_landmarks):
                self.mp_drawing.draw_landmarks(
                        image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return image