import mysql.connector
from common.constants.datasource_constants import HOST, USER_NAME, PASSWORD, DATABASE
from common.constants.app_constants import CLASSIFIERS, TRADING_WINDOWS, FORWARD_DAYS


def get_predictions(request):
    mydb = mysql.connector.connect(
        host=HOST, user=USER_NAME, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()

    query = 'SELECT * FROM prediction WHERE `COMPANY_SYMBOL` = "%s"' % request.args['symbol']
    mycursor.execute(query)
    data = mycursor.fetchall()
    response = {
        "companySymbol": request.args['symbol'],
        "predictions": []
    }
    for row in data:
        response['predictions'].append({
            'label': row[3],
            'accuracy': row[4],
            'classifier': row[1],
            'tradingWindow': row[2],
            'forwardDay': 1,
        })
        response['predictions'].append({
            'label': row[5],
            'accuracy': row[6],
            'classifier': row[1],
            'tradingWindow': row[2],
            'forwardDay': 3,
        })
        response['predictions'].append({
            'label': row[7],
            'accuracy': row[8],
            'classifier': row[1],
            'tradingWindow': row[2],
            'forwardDay': 5,
        })

    mycursor.close()
    mydb.close()
    return response


def update_prediction(prediction):
    mydb = mysql.connector.connect(
        host=HOST, user=USER_NAME, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()

    prediction_statement = "UPDATE prediction SET `PREDICTION_LABEL_1` = %s, Prediction_accuracy_1 = %s, `PREDICTION_LABEL_3` = %s, `PREDICTION_ACCURACY_3` = %s, `PREDICTION_LABEL_5` = %s, `PREDICTION_ACCURACY_5` = %s WHERE `COMPANY_SYMBOL` = %s AND `TRADING_WINDOW` = %s AND `CLASSIFIER` = %s"
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
