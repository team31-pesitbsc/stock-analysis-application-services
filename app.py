import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
import pickle
from flask import Flask, request, jsonify
from common.constants.app_constants import TRADING_WINDOWS, FORWARD_DAYS, CLASSIFIERS
from common.subroutines.feature_extraction import calculate_rsi, calculate_k_r, calculate_proc, calculate_obv, ema, fmacd
from common.exceptions import StockUpdateException
from repository import company_repository, stock_repository, prediction_repository, feature_repository
import os

app = Flask(__name__)

# ROUTES
@app.route("/")
def root():
    return "Welcome to the stock analysis application running in "+os.getenv('ENVIRONMENT')+"!"

# STOCK ROUTES
@app.route("/stocks")
def get_stocks():
    query_params = {
        "symbol": request.args['symbol'],
        "limit": int(request.args['limit']),
        "offset": int(request.args['offset'])
    }
    response = stock_repository.get_stocks(query_params)
    return jsonify(response)


@app.route("/stocks", methods=['POST'])
def add_stock():

    stock_repository.add_stock(request)
    query_params = {
        "symbol": request.form.get("symbol"),
        "limit": max(TRADING_WINDOWS),
        "offset": 0
    }
    stock_data = stock_repository.get_stocks(query_params)["stocks"]

    # FEATURE EXTRACTION
    C = float(request.form.get("close"))
    rsi = calculate_rsi(stock_data[:14])
    K, R = calculate_k_r(stock_data[:14], C)
    for trading_window in TRADING_WINDOWS:
        proc = calculate_proc(stock_data, trading_window, C)
        query_params = {
            'symbol': request.form.get("symbol"),
            'tradingWindow': str(trading_window),
            'sortDirection': 'DESC',
            'limit': max(TRADING_WINDOWS),
            'offset': 0

        }
        previous_features = feature_repository.get_features(query_params)
        obv = calculate_obv(previous_features, stock_data, C, int(
            request.form.get("volume")), trading_window)
        ema_12, ema_26, macd = fmacd(previous_features, C)
        ema_9_macd = ema(9, previous_features[0][12], macd)
        if(macd >= ema_9_macd):
            buy_sell = 1
        else:
            buy_sell = -1

        class_label = 1
        if C < stock_data[trading_window - 1]["close"]:
            class_label = -1

        # PREDICTION
        if request.form.get("updatePrediction") == "True":
            for classifier_name in CLASSIFIERS:
                for forward_day in FORWARD_DAYS:
                    data_train = pd.DataFrame(
                        [[trading_window, forward_day, rsi, K, R, buy_sell, proc, obv]])
                    with open("trained-models/%(classifier_name)s_model.dump" % {'classifier_name': classifier_name}, "rb") as f:
                        model = pickle.load(f)
                        prediction = model.predict(data_train)[0]
                        probability = max(
                            list(model.predict_proba(data_train))[0])
                        prediction_data = {
                            'label': str(prediction),
                            'probability': str(probability),
                            'forwardDay': str(forward_day),
                            'symbol': request.form.get("symbol"),
                            'tradingWindow': str(trading_window),
                            'classifierName': classifier_name
                        }
                        prediction_repository.update_prediction(
                            prediction_data)

        # FEATURE DB INSERTION
        feature_data = {
            "symbol": request.form.get("symbol"),
            "date": request.form.get("date"),
            'tradingWindow': str(trading_window),
            'rsi': str(rsi),
            'K': str(K),
            'R': str(R),
            'buySell': str(buy_sell),
            'proc': str(proc),
            'obv': str(obv),
            'classLabel': str(class_label),
            'ema12': str(ema_12),
            'ema26': str(ema_26),
            'ema9macd': str(ema_9_macd),
        }
        feature_repository.add_feature(feature_data)

    return "Inserted stock and feature data into DB"


@app.route("/stocks", methods=['PUT'])
def update_stock():
    query_params = {
        "symbol": request.form.get("symbol"),
        "limit": 2,
        "offset": 0
    }
    latest_stock = stock_repository.get_stocks(query_params)['stocks'][0]
    # TODO - find better way to compare dates
    if str(request.form.get('date')) == str(latest_stock['date']):
        stock_repository.update_stock(request)
        return "Updated stock data"
    else:
        raise StockUpdateException(latest_stock['date'],
                                   request.form.get('date'))


# COMPANY ROUTES
@app.route("/companies")
def get_companies():
    companies = company_repository.get_companies()
    return jsonify(companies)

# PREDICTION ROUTES
@app.route("/predictions")
def get_predictions():
    response = prediction_repository.get_predictions(request)
    return jsonify(response)


# TRAIN ROUTES
@app.route("/train")
def train():

    columns = ["COMPANY_SYMBOL", "DATE", "TRADING_WINDOW", "RSI", "K",
               "R", "SL", "PROC", "OBV", "LABEL", "x", "y", "z"]

    training_data = pd.DataFrame(columns=columns)
    companies = company_repository.get_companies()
    for company in companies:
        for trading_window in TRADING_WINDOWS:
            query_params = {
                'symbol': company["symbol"],
                'tradingWindow': str(trading_window),
                'sortDirection': "ASC",
            }
            data = feature_repository.get_features(query_params)
            data = pd.DataFrame(data, columns=columns)
            for forward_day in FORWARD_DAYS:
                forward_day_data = data.copy()
                forward_day_data.LABEL = forward_day_data.LABEL.shift(
                    -1*forward_day)
                forward_day_data = forward_day_data[:-1*forward_day]
                forward_day_data.insert(3, 'Forward_day', forward_day)
                training_data = training_data.append(
                    forward_day_data, ignore_index=True, sort=True)

    x_train = training_data[["TRADING_WINDOW", "Forward_day", "RSI",
                             "K", "R", "SL", "PROC", "OBV"]]
    y_train = training_data[["LABEL"]]

    for classifier_name, classifier in CLASSIFIERS.items():
        model = classifier.fit(x_train, y_train.values.ravel())
        print(classifier_name + ":" +
              str(model.score(x_train, y_train.values.ravel())))
        with open("trained-models/%(classifier_name)s_model.dump" % {"classifier_name": classifier_name}, "wb") as f:
            pickle.dump(model, f)
    return "Trained Model"


if __name__ == '__main__':
    app.run(host="0.0.0.0")
