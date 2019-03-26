from interface import implements
from common.classifiers.interface import IHybridClassifier


class HybridClassifier(implements(IHybridClassifier)):

    # TODO - figure out how to implement this thing
    def __init__(self):
        pass

    def fit(self, x, y):
        pass

    def score(self, x, y):
        pass

    def predict(self, x):
        pass

    def predict_proba(self, x):
        pass
