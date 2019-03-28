from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from common.classifiers.implementation import HybridClassifier
# CONSTANTS
TRADING_WINDOWS = [3, 5, 15, 30, 60, 90]
FORWARD_DAYS = [1, 3, 5]
CLASSIFIERS = {
    "RF": RandomForestClassifier(n_estimators=100, max_depth=10),
    "GBDT": GradientBoostingClassifier(n_estimators=100, max_depth=10, loss="exponential")
    "HYBRID": HybridClassifier(rf_params = {'n_estimators':100, 'max_depth':10}, gbdt_params = {'n_estimators':100, 'max_depth':10, 'loss':'exponential'})
}
