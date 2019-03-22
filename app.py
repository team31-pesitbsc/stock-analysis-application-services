from pprint import pprint
import mysql.connector
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score
import pickle
from flask import Flask, request, jsonify

app = Flask(__name__)
trading_windows = [3, 5, 15, 30, 60, 90]
forward_days = [1, 3, 5]

# FEATURE EXTRACTION FUNCTIONS TODO-Move functions to different file


def calculate_rsi(data):
    avggain = 0
    avgloss = 0
    for i in range(0, len(data)-1):
        diff = data[i][3] - data[i+1][3]
        if diff < 0:
            avgloss += diff*(-1)
        elif diff > 0:
            avggain += diff
    avggain /= 14.0
    avgloss /= 14.0
    rsi = 0
    if avgloss != 0:
        rsi = 100 - 100 / (1 + (avggain/avgloss))
    return rsi


def calculate_k_r(data, C):
    H_14 = max([row[4] for row in data])
    L_14 = min([row[5] for row in data])
    K = 0
    R = 0
    if (H_14 - L_14) != 0:
        K = 100*((C - L_14)/(H_14 - L_14))
        R = -100*((H_14 - C)/(H_14 - L_14))
    return K, R


def calculate_proc(data, period, C):
    proc = 0
    if data[period-1][3] != 0:
        proc = (C - data[period - 1][3]) / data[period-1][3]
    return proc


def calculate_obv(features, history, C, volume, trading_window):
    obv = features[trading_window-1][8]
    if C > history[trading_window-1][3]:
        obv = obv + volume
    elif C < history[trading_window-1][3]:
        obv = obv - volume
    return obv


def fmacd(features, C):
    ema_12 = ema(12, features[0][10], C)
    ema_26 = ema(26, features[0][11], C)
    return ema_12, ema_26, (ema_12 - ema_26)


def ema(n, prev_ema, X):
    weight = 2.0/(n + 1.0)
    ema = (X - prev_ema)*weight + prev_ema
    return ema

# ROUTE FUNCTIONS


@app.route("/")
def root():
    return "You have hit root route"


@app.route("/insertStock", methods=['POST'])
def insert_history():
    mydb = mysql.connector.connect(
        host="localhost", user="root", passwd="root", database="stock")
    mycursor = mydb.cursor()

    print(request.form.get("Date"))
    # STOCK QUOTE DB INSERTION
    stock_statement = "INSERT INTO stock VALUES (%s, %s, %s, %s, %s, %s, %s)"
    stock_data = (
        request.form.get("Symbol"),
        request.form.get("Date"),
        request.form.get("Open"),
        request.form.get("Close"),
        request.form.get("High"),
        request.form.get("Low"),
        request.form.get("Volume"),
    )
    mycursor.execute(stock_statement, stock_data)
    mydb.commit()
    # STOCK QUOTE DB INSERTION

    required_days = max(trading_windows)
    statement = 'SELECT * FROM stock '
    statement += 'WHERE Stock_symbol = "'+request.form.get("Symbol")+'" '
    statement += 'ORDER BY Stock_date DESC LIMIT '+str(required_days)
    mycursor.execute(statement)
    stock_data = mycursor.fetchall()

    # FEATURE EXTRACTION
    C = float(request.form.get("Close"))
    rsi = calculate_rsi(stock_data[:14])
    K, R = calculate_k_r(stock_data[:14], C)
    for trading_window in trading_windows:
        proc = calculate_proc(stock_data, trading_window, C)
        statement = 'SELECT * FROM features '
        statement += 'WHERE Feature_symbol = "'+request.form.get("Symbol")+'" '
        statement += 'AND Trading_window = "'+str(trading_window)+'" '
        statement += 'ORDER BY Feature_date DESC LIMIT '+str(required_days)
        mycursor.execute(statement)
        previous_features = mycursor.fetchall()
        obv = calculate_obv(previous_features, stock_data, C, int(
            request.form.get("Volume")), trading_window)
        ema_12, ema_26, macd = fmacd(previous_features, C)
        ema_9_macd = ema(9, previous_features[0][12], macd)
        if(macd >= ema_9_macd):
            buy_sell = 1
        else:
            buy_sell = -1

        class_label = 1
        if C < stock_data[trading_window - 1][3]:
            class_label = -1

        # RF PREDICTION UPDATION
        rf_prediction = {}
        rf_accuracy = {}
        for forward_day in forward_days:
            data_train = pd.DataFrame(
                [[trading_window, forward_day, rsi, K, R, buy_sell, proc, obv]])
            with open("rf_model.dump", "rb") as f:
                rf = pickle.load(f)
                rf_prediction[forward_day] = rf.predict(data_train)[0]
                rf_accuracy[forward_day] = max(
                    list(rf.predict_proba(data_train))[0])

        prediction_statement = "UPDATE prediction SET Prediction_label_1 = %s, Prediction_accuracy_1 = %s, "
        prediction_statement += "Prediction_label_3 = %s, Prediction_accuracy_3 = %s, "
        prediction_statement += "Prediction_label_5 = %s, Prediction_accuracy_5 = %s "
        prediction_statement += "WHERE Prediction_symbol = %s AND Trading_window = %s AND Classifier = 'RF'"
        prediction_data = (
            str(rf_prediction[1]),
            str(rf_accuracy[1]),
            str(rf_prediction[3]),
            str(rf_accuracy[3]),
            str(rf_prediction[5]),
            str(rf_accuracy[5]),
            request.form.get("Symbol"),
            str(trading_window)
        )
        mycursor.execute(prediction_statement, prediction_data)
        mydb.commit()
        # RF PREDICTION UPDATION

        # GBDT PREDICTION UPDATION
        gbdt_prediction = {}
        gbdt_accuracy = {}
        for forward_day in forward_days:
            data_train = pd.DataFrame(
                [[trading_window, forward_day, rsi, K, R, buy_sell, proc, obv]])
            with open("gbdt_model.dump", "rb") as f:
                gbdt = pickle.load(f)
                gbdt_prediction[forward_day] = gbdt.predict(data_train)[0]
                gbdt_accuracy[forward_day] = max(
                    list(gbdt.predict_proba(data_train))[0])

        prediction_statement = "UPDATE prediction SET Prediction_label_1 = %s, Prediction_accuracy_1 = %s, "
        prediction_statement += "Prediction_label_3 = %s, Prediction_accuracy_3 = %s, "
        prediction_statement += "Prediction_label_5 = %s, Prediction_accuracy_5 = %s "
        prediction_statement += "WHERE Prediction_symbol = %s AND Trading_window = %s AND Classifier = 'GBDT'"
        prediction_data = (
            str(gbdt_prediction[1]),
            str(gbdt_accuracy[1]),
            str(gbdt_prediction[3]),
            str(gbdt_accuracy[3]),
            str(gbdt_prediction[5]),
            str(gbdt_accuracy[5]),
            request.form.get("Symbol"),
            str(trading_window)
        )
        mycursor.execute(prediction_statement, prediction_data)
        mydb.commit()
        # GBDT PREDICTION UPDATION

        # FEATURE DB INSERTION
        feature_statement = "INSERT INTO features VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        feature_data = (
            request.form.get("Symbol"),
            request.form.get("Date"),
            str(trading_window),
            str(rsi),
            str(K),
            str(R),
            str(buy_sell),
            str(proc),
            str(obv),
            str(class_label),
            str(ema_12),
            str(ema_26),
            str(ema_9_macd)
        )
        mycursor.execute(feature_statement, feature_data)
        mydb.commit()
        # FEATURE DB INSERTION

    mycursor.close()
    mydb.close()
    return "Inserted stock and feature data into DB"


@app.route("/updateLive", methods=['POST'])
def update_live():
    mydb = mysql.connector.connect(
        host="localhost", user="root", passwd="root", database="stock")
    mycursor = mydb.cursor()

    required_days = max(trading_windows)
    statement = 'SELECT * FROM stock '
    statement += 'WHERE Stock_symbol = "'+request.form.get("Symbol")+'" '
    statement += 'ORDER BY Stock_date DESC LIMIT '+str(required_days)
    mycursor.execute(statement)

    mydb.commit()
    live_statement = "UPDATE stock"
    live_statement += " SET Stock_close = %s, Stock_high = %s, Stock_low = %s, Stock_volume = %s"
    live_statement += " WHERE Stock_symbol = %s"
    live_statement += " AND Stock_date = %s"
    live_data = (
        request.form.get("Current"),
        request.form.get("High"),
        request.form.get("Low"),
        request.form.get("Volume"),
        request.form.get("Symbol"),
        request.form.get("Date")
    )
    # update live data
    mycursor.execute(live_statement, live_data)
    mydb.commit()

    mycursor.close()
    mydb.close()
    return "Inserted live data into DB"


@app.route("/companies")
def get_companies():
    mydb = mysql.connector.connect(
        host="localhost", user="root", passwd="root", database="stock")
    mycursor = mydb.cursor()

    statement = "SELECT * FROM company"
    mycursor.execute(statement)
    data = mycursor.fetchall()
    companies = []
    for row in data:
        companies.append({"companySymbol": row[0], "companyName": row[1]})

    mycursor.close()
    mydb.close()
    return jsonify(companies)


@app.route("/stocks/<stock_symbol>")
def get_stock(stock_symbol):
    mydb = mysql.connector.connect(
        host="localhost", user="root", passwd="root", database="stock")
    mycursor = mydb.cursor()

    statement = "SELECT * FROM stock "
    statement += 'WHERE Stock_symbol = "' + stock_symbol + '" '
    statement += "ORDER BY Stock_date DESC LIMIT " + \
        request.args['limit']+" OFFSET " + request.args['offset']

    mycursor.execute(statement)
    data = mycursor.fetchall()

    stocks = []
    for row in data:
        stocks.append({
            "companySymbol": row[0],
            "stockDate": row[1],
            "stockOpen": row[2],
            "stockClose": row[3],
            "stockHigh": row[4],
            "stockLow": row[5],
            "stockVolume": row[6],
        })

    mycursor.close()
    mydb.close()
    return jsonify(stocks)


@app.route("/predictions/<prediction_symbol>")
def get_live(prediction_symbol):
    mydb = mysql.connector.connect(
        host="localhost", user="root", passwd="root", database="stock")
    mycursor = mydb.cursor()

    statement = 'SELECT * FROM prediction'
    statement += ' WHERE Prediction_symbol = "' + prediction_symbol + '"'
    mycursor.execute(statement)
    data = mycursor.fetchall()

    predictions = []
    for row in data:
        predictions.append({
            "companySymbol": row[0],
            "Classifier":row[1],
            "TradingWindow": row[2],
            "predictionLabel1": row[3],
            "predictionAccuracy1": row[4],
            "predictionLabel3": row[5],
            "predictionAccuracy3": row[6],
            "predictionLabel5": row[7],
            "predictionAccuracy5": row[8],
        })

    mycursor.close()
    mydb.close()
    return jsonify(predictions)


@app.route("/train")
def train(error_day=-1):

    columns = ["Feature_symbol", "Feature_date", "Trading_window", "Feature_RSI", "Feature_K",
               "Feature_R", "Feature_SL", "Feature_PROC", "Feature_OBV", "Feature_label", "x", "y", "z"]
    mydb = mysql.connector.connect(
        host="localhost", user="root", passwd="root", database="stock")
    mycursor = mydb.cursor()

    training_data = pd.DataFrame(columns=columns)
    statement = "SELECT * FROM company"
    mycursor.execute(statement)
    companies = mycursor.fetchall()
    for company in companies:
        for trading_window in trading_windows:
            statement = "SELECT * FROM features "
            statement += "WHERE Trading_window = " + \
                str(trading_window)+" AND Feature_symbol = '"+company[0]+"' "
            statement += "ORDER BY Feature_date"
            mycursor.execute(statement)
            data = mycursor.fetchall()
            data = pd.DataFrame(data, columns=columns)
            for forward_day in forward_days:
                forward_day_data = data.copy()
                forward_day_data.Feature_label = forward_day_data.Feature_label.shift(
                    -1*forward_day)
                forward_day_data = forward_day_data[:-1*forward_day]
                forward_day_data.insert(3, 'Forward_day', forward_day)
                training_data = training_data.append(
                    forward_day_data, ignore_index=True, sort=True)

    x_train = training_data[["Trading_window", "Forward_day", "Feature_RSI",
                             "Feature_K", "Feature_R", "Feature_SL", "Feature_PROC", "Feature_OBV"]]
    y_train = training_data[["Feature_label"]]
    rf = RandomForestClassifier(n_estimators=100, max_depth=10)
    gbdt = GradientBoostingClassifier(
        n_estimators=100, max_depth=10, loss="exponential")
    rf.fit(x_train, y_train.values.ravel())
    gbdt.fit(x_train, y_train)

    print(rf.score(x_train, y_train))
    print(gbdt.score(x_train, y_train))
    with open("rf_model.dump", "wb") as f:
        pickle.dump(rf, f)
    with open("gbdt_model.dump", "wb") as f:
        pickle.dump(gbdt, f)

    mycursor.close()
    mydb.close()
    return "Trained Model"


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
