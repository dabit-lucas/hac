class ActionDetector:
    """
    init: 
        model: trained model 
        pred2str: a function convert predictions to string
    """

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

    def __init__(self, model):
        self.model = model
        self.target_columns = [key + "_x" for key in self.W_LIST_POSE] + [key + "_y" for key in self.W_LIST_POSE]

    def __call__(self, df):
        """
        input:
            x: inputs for model to predict hand gesture, the type of x depends on the model.
        output:
            output: hand gesture like "one", "two", "three", "stone"...

        """
        df = df[self.target_columns].dropna()
        df = df.apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=1)

        pred = self.model.predict(df.values)
        output = self.pred2str(pred)

        return output

    def pred2str(self, pred):
        """
        input:
            pred: prediction result from the model
        output:
            output: pose like "stand", "jump"...
        """
        pass

class SkeletonBasedActionDetector(ActionDetector):

    def pred2str(self, pred):

        mapping = ["lift", "punch", "trample", "sit"]

        return mapping[pred[0]]