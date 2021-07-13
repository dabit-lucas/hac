import os
import pathlib
import pickle
from ..utils.key_points import W_LIST_POSE, W2I_POSE, W_LIST_LEFT_HAND, W2I_LEFT_HAND, W_LIST_RIGHT_HAND, W2I_RIGHT_HAND

class ActionDetector:
    """
    init: 
        model: trained model 
        pred2str: a function convert predictions to string
    """

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
        pred = self.model.predict(data)
        output = self.pred2str(pred)
        print(output)

        return output

    def pred2str(self, pred):
        """
        input:
            pred: prediction result from the model
        output:
            output: pose like "stand", "jump"...
        """
        pass

    def normalize(self, df):
        df = df.copy()
        df = df[self.target_columns].fillna(0)
        df = df[self.target_columns].dropna()
        df = df.apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=1)
        df = df.fillna(0)
        return df.values

class RobloxLiftGameActionDetector(ActionDetector):

    def __init__(self):
        model_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "..\\model\\roblox_lift_game\\model.pth")
        model = pickle.load(open(model_path, 'rb'))
        super(RobloxLiftGameActionDetector, self).__init__(model)

    def pred2str(self, pred):
        mapping = ["walk", "jump", "hands_on_hips", "point_left", "point_right", "arms_lift", "punch", "trample", "lateral_raise", "stand"]
        return mapping[pred[0]]