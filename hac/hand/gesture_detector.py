class GestureDetector:

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

    def __init__(self, model):

        """
        init: 
            model: trained model 
            pred2str: a function convert predictions to string
        """
        self.model = model
        self.target_columns = [key + "_x" for key in self.W_LIST_RIGHT_HAND] + [key + "_y" for key in self.W_LIST_RIGHT_HAND]
        #self.pred2str = pred2str

    def __call__(self, df):
        """
        input:
            x: inputs for model to predict hand gesture, the type of x depends on the model.
        output:
            output: hand gesture like "one", "two", "three", "stone"...

        """
        try:
            df = df[self.target_columns].dropna()
            df = df.apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=1)
            x = df[self.target_columns].values
            pred = self.model.predict(x)
            output = self.pred2str(pred)
        except:
            return "None"

        return output

    def pred2str(self, pred):
        """
        input:
            pred: prediction result from the model
        output:
            output: hand gesture like "one", "two", "three", "stone"...
        """
        pass

class SkeletonBasedGestureDetector(GestureDetector):

    def pred2str(self, pred):

        mapping = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "None"]

        return mapping[pred[0]]