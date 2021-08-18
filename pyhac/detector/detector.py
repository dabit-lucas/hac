import os 
import pathlib
import pickle
import torch
from ..utils.key_points import W_LIST_POSE, W2I_POSE, W_LIST_LEFT_HAND, W2I_LEFT_HAND, W_LIST_RIGHT_HAND, W2I_RIGHT_HAND
from ..utils.normalizer import normalize_data, normalize_hand_data
from ..model import HACModel

class Detector:

    def __init__(self, model_data):

        """
        init: 
            model: trained model 
            pred2str: a function convert predictions to string
        """
        self.model = model_data["model"]
        self.target_columns = model_data["target_columns"]
        self.mapping = model_data["actions"]
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def __call__(self, df):
        """
        input:
            x: inputs for model to predict hand gesture, the type of x depends on the model.
        output:
            output: hand gesture like "one", "two", "three", "stone"...

        """
        data = self.normalize(df)
        x = torch.from_numpy(data).view(-1, self.model.in_channels, self.model.get_num_vertices(), 1).float().to(self.device)
        output = self.model(x) # batch, (x, y), num of joints, t
        pred = output.reshape(-1, len(self.mapping)).cpu().argmax(axis=1, keepdim=True)
        pred_gesture = self.pred2str(pred)
        print(pred_gesture)

        return pred_gesture

    def pred2str(self, pred):
        """
        input:
            pred: prediction result from the model
        output:
            output: hand gesture like "one", "two", "three", "stone"...
        """
        return self.mapping[pred[0]]

    def normalize(self, df):
        if self.model.get_num_vertices() == 75: # hand + pose
            df = normalize_data(df)
        else:
            df = normalize_hand_data(df)
        return df.values