import mysql.connector
from common.constants.datasource_constants import HOST, USER_NAME, PASSWORD, DATABASE
from common.constants.app_constants import CLASSIFIERS, TRADING_WINDOWS, FORWARD_DAYS


def get_predictions(request):
    mydb = mysql.connector.connect(
        host=HOST, user=USER_NAME, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()

    query = 'SELECT * FROM prediction WHERE Prediction_symbol = "%s"' % request.args['symbol']
    mycursor.execute(query)
    data = mycursor.fetchall()

    response = {
        "companySymbol": request.args['symbol'],
        "predictions": {
            classifier_name: {
                trading_window: {
                    forward_day: {
                        'label': None,
                        'accuracy': None
                    } for forward_day in FORWARD_DAYS
                } for trading_window in TRADING_WINDOWS
            } for classifier_name in CLASSIFIERS
        }
    }

    for row in data:
        response['predictions'][row[1]][row[2]][1]['label'] = row[3]
        response['predictions'][row[1]][row[2]][1]['accuracy'] = row[4]

        response['predictions'][row[1]][row[2]][3]['label'] = row[5]
        response['predictions'][row[1]][row[2]][3]['accuracy'] = row[6]

        response['predictions'][row[1]][row[2]][5]['label'] = row[7]
        response['predictions'][row[1]][row[2]][5]['accuracy'] = row[8]

    mycursor.close()
    mydb.close()
    return response


def update_prediction(prediction):
    mydb = mysql.connector.connect(
        host=HOST, user=USER_NAME, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()

    prediction_statement = "UPDATE prediction SET Prediction_label_1 = %s, Prediction_accuracy_1 = %s, Prediction_label_3 = %s, Prediction_accuracy_3 = %s, Prediction_label_5 = %s, Prediction_accuracy_5 = %s WHERE Prediction_symbol = %s AND Trading_window = %s AND Classifier = %s"
    prediction_data = (
        prediction['label1'],
        prediction['accuracy1'],
        prediction['label3'],
        prediction['accuracy3'],
        prediction['label5'],
        prediction['accuracy5'],
        str(prediction['symbol']),
        prediction['tradingWindow'],
        str(prediction['classifierName'])
    )
    mycursor.execute(prediction_statement, prediction_data)
    mydb.commit()
    mycursor.close()
    mydb.close()