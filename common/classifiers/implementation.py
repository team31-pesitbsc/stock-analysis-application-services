from interface import implements
from common.classifiers.interface import IHybridClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import pandas as pd


class HybridClassifier(implements(IHybridClassifier)):
    rf = None
    gbdt = None

    def __init__(self, rf_params={'n_estimators': 100, 'max_depth': 10}, gbdt_params={'n_estimators': 100, 'max_depth': 10, 'loss': 'exponential'}):
        self.rf = RandomForestClassifier(
            n_estimators=rf_params['n_estimators'], max_depth=rf_params['max_depth'])
        self.gbdt = GradientBoostingClassifier(
            n_estimators=gbdt_params['n_estimators'], max_depth=gbdt_params['max_depth'], loss=gbdt_params['loss'])

    def fit(self, x, y):
        self.rf.fit(x, y)
        rf_pred = pd.DataFrame(self.rf.predict(x))
        x_merged = pd.concat([x, rf_pred], axis=1)
        self.gbdt.fit(x_merged, y)
        return self

    def score(self, x, y):
        rf_pred = pd.DataFrame(self.rf.predict(x))
        x_merged = pd.concat([x, rf_pred], axis=1)
        return self.gbdt.score(x_merged, y)

    def predict(self, x):
        rf_pred = pd.DataFrame(self.rf.predict(x))
        x_merged = pd.concat([x, rf_pred], axis=1)
        return self.gbdt.predict(x_merged)

    def predict_proba(self, x):
        rf_pred = pd.DataFrame(self.rf.predict(x))
        x_merged = pd.concat([x, rf_pred], axis=1)
        return self.gbdt.predict_proba(x_merged)
