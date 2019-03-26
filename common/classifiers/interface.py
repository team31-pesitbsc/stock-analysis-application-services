from interface import Interface


class IHybridClassifier(Interface):

    def fit(self, x, y):
        pass

    def score(self, x, y):
        pass

    def predict(self, x):
        pass

    def predict_proba(self, x):
        pass
