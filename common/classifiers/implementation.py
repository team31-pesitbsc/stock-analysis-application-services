from interface import implements
from common.classifiers.interface import IHybridClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier


class HybridClassifier(implements(IHybridClassifier)):
    rf = None
    gbdt = None
    
    def __init__(self, rf_params = {'n_estimators':100, 'max_depth':10}, gbdt_params = {'n_estimators':100, 'max_depth':10, 'loss':'exponential'}):
        rf = RandomForestClassifier(n_estimators=rf_params['n_estimators'], max_depth=rf_params['max_depth'])
        gbdt = GradientBoostingClassifier(n_estimators=gbdt_params['n_estimators'], max_depth=gbdt_params['max_depth'], loss=gbdt_params['loss'])
        
    def fit(self, x, y):
        rf.fit(x,y)
        rf_pred = rf.predict(x)
        # TODO - create x_merged by append rf_pred as last column to x
        x_merged = x
        gbdt.fit(x_merged, y)
        return self

    def score(self, x, y):
        rf_pred = rf.predict(x)
        # TODO - create x_merged by append rf_pred as last column to x
        x_merged = x
        return gbdt.score(x_merged, y)

    def predict(self, x):
        rf_pred = rf.predict(x)
        # TODO - create x_merged by append rf_pred as last column to x
        x_merged = x
        return gbdt.predict(x_merged)

    def predict_proba(self, x):
        rf_pred = rf.predict(x)
        # TODO - create x_merged by append rf_pred as last column to x
        x_merged = x
        return gbdt.predict_proba(x_merged)
