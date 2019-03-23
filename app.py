import mysql.connector
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import precision_score, recall_score, f1_score
import pickle
from flask import Flask, request, jsonify
from common.constants.app_constants import TRADING_WINDOWS, FORWARD_DAYS, CLASSIFIERS
from common.constants.datasource_constants import HOST, USER_NAME, PASSWORD, DATABASE
from common.subroutines.feature_extraction import calculate_rsi, calculate_k_r, calculate_proc, calculate_obv, ema, fmacd
from repository import company_repository, stock_repository, prediction_repository
app = Flask(__name__)

# ROUTES


@app.route("/")
def root():
    return "Welcome to the stock analysis application"

# STOCK ROUTES


@app.route("/stocks")
def get_stocks():
    response = stock_repository.get_stocks(request)
    return jsonify(response)


@app.route("/stocks", methods=['POST'])
def insert_stock():
    mydb = mysql.connector.connect(
        host=HOST, user=USER_NAME, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()

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

    required_days = max(TRADING_WINDOWS)
    statement = 'SELECT * FROM stock '
    statement += 'WHERE Stock_symbol = "'+request.form.get("Symbol")+'" '
    statement += 'ORDER BY Stock_date DESC LIMIT '+str(required_days)
    mycursor.execute(statement)
    stock_data = mycursor.fetchall()

    # FEATURE EXTRACTION
    C = float(request.form.get("Close"))
    rsi = calculate_rsi(stock_data[:14])
    K, R = calculate_k_r(stock_data[:14], C)
    for trading_window in TRADING_WINDOWS:
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

        # PREDICTION
        for classifier_name in CLASSIFIERS:
            prediction = {}
            accuracy = {}
            for forward_day in FORWARD_DAYS:
                data_train = pd.DataFrame(
                    [[trading_window, forward_day, rsi, K, R, buy_sell, proc, obv]])
                with open("trained-models/%(classifier_name)s_model.dump" % {'classifier_name': classifier_name}, "rb") as f:
                    model = pickle.load(f)
                    prediction[forward_day] = model.predict(data_train)[0]
                    accuracy[forward_day] = max(
                        list(model.predict_proba(data_train))[0])

            prediction_statement = "UPDATE prediction SET Prediction_label_1 = %s, Prediction_accuracy_1 = %s, "
            prediction_statement += "Prediction_label_3 = %s, Prediction_accuracy_3 = %s, "
            prediction_statement += "Prediction_label_5 = %s, Prediction_accuracy_5 = %s "
            prediction_statement += "WHERE Prediction_symbol = %s AND Trading_window = %s AND Classifier = %s"
            prediction_data = (
                str(prediction[1]),
                str(accuracy[1]),
                str(prediction[3]),
                str(accuracy[3]),
                str(prediction[5]),
                str(accuracy[5]),
                request.form.get("Symbol"),
                str(trading_window),
                classifier_name
            )
            mycursor.execute(prediction_statement, prediction_data)
            mydb.commit()

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


@app.route("/stocks", methods=['PUT'])
def update_stock():
    # TODO - update stock only if it is live or throw error
    stock_repository.update_stock(request)
    return "Updated Live data"

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


@app.route("/train")
def train():

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
        for trading_window in TRADING_WINDOWS:
            statement = "SELECT * FROM features "
            statement += "WHERE Trading_window = " + \
                str(trading_window)+" AND Feature_symbol = '"+company[0]+"' "
            statement += "ORDER BY Feature_date"
            mycursor.execute(statement)
            data = mycursor.fetchall()
            data = pd.DataFrame(data, columns=columns)
            for forward_day in FORWARD_DAYS:
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

    for classifier_name, classifier in CLASSIFIERS.items():
        model = classifier.fit(x_train, y_train.values.ravel())
        print(model.score(x_train, y_train.values.ravel()))
        with open("trained-models/%(classifier_name)s_model.dump" % {"classifier_name": classifier_name}, "wb") as f:
            pickle.dump(model, f)

    mycursor.close()
    mydb.close()
    return "Trained Model"


if __name__ == '__main__':
    app.run(host="192.168.2.6", debug=True)
