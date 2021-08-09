import os
import pathlib
import pickle
import torch
from ..utils.key_points import W_LIST_POSE, W2I_POSE, W_LIST_LEFT_HAND, W2I_LEFT_HAND, W_LIST_RIGHT_HAND, W2I_RIGHT_HAND
from ..utils.normalizer import normalize_data
from ..model import HACModel

class ActionDetector:
    """
    init: 
        model: trained model 
        pred2str: a function convert predictions to string
    """
    num_vertices = 33 + 21 * 2
    in_channels = 3

    def __init__(self, model):
        
        self.model = model
        self.target_columns = [key + "_x" for key in W_LIST_RIGHT_HAND] + [key + "_y" for key in W_LIST_RIGHT_HAND]
        self.target_columns += [key + "_x" for key in W_LIST_LEFT_HAND] + [key + "_y" for key in W_LIST_LEFT_HAND]
        self.target_columns += [key + "_x" for key in W_LIST_POSE] + [key + "_y" for key in W_LIST_POSE]

    def __call__(self, df):
        """
        input:
            x: inputs for model to predict hand gesture, the type of x depends on the model.
        output:
            output: hand gesture like "one", "two", "three", "stone"...
        """
        data = self.normalize(df)
        x = torch.from_numpy(data).view(-1, self.in_channels, self.num_vertices, 1).float().to(self.device)
        output = self.model(x) # batch, (x, y), num of joints, t
        pred = output.reshape(-1, len(self.mapping)).cpu().argmax(axis=1, keepdim=True)
        pred_action = self.pred2str(pred)
        print(pred_action)

        return pred_action

    def pred2str(self, pred):
        """
        input:
            pred: prediction result from the model
        output:
            output: pose like "stand", "jump"...
        """
        pass
    
    def normalize(self, df):
        df = normalize_data(df)
        return df.values

    '''
    def normalize(self, df):
        df = df.copy()
        df = df[self.target_columns].fillna(0)
        df = df[self.target_columns].dropna()
        df = df.apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=1)
        df = df.fillna(0)
        return df.values
    '''

class RobloxLiftGameActionDetector(ActionDetector):

    mapping = ["walk", "jump", "hands_on_hips", "point_left", "point_right", "arms_lift", "punch", "trample", "lateral_raise", "stand"]
    
    def __init__(self):

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        num_class = len(self.mapping)
        model = HACModel(in_channels=3, num_class=num_class, k_hop=2, mode="pose_hand").to(self.device)
        model_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "..\\trained_model\\gcn\\actions\\best_model.pth")
        model.load_state_dict(torch.load(model_path, map_location=torch.device(self.device)))
        model.eval()
        super(RobloxLiftGameActionDetector, self).__init__(model)
    
    def pred2str(self, pred):
        
        return self.mapping[pred[0]]