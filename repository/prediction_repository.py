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
            'label': row[4],
            'probability': row[5],
            'classifier': row[1],
            'tradingWindow': row[2],
            'forwardDay': row[3],
        })

    mycursor.close()
    mydb.close()
    return response


def update_prediction(prediction):
    mydb = mysql.connector.connect(
        host=HOST, user=USER_NAME, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()

    prediction_statement = "UPDATE prediction SET `LABEL` = %s, `PROBABILITY` = %s WHERE `COMPANY_SYMBOL` = %s AND `TRADING_WINDOW` = %s AND `CLASSIFIER` = %s AND `FORWARD_DAY` = %s"
    prediction_data = (
        prediction['label'],
        prediction['probability'],
        prediction['symbol'],
        prediction['tradingWindow'],
        prediction['classifierName'],
        prediction['forwardDay']
    )
    mycursor.execute(prediction_statement, prediction_data)
    mydb.commit()
    mycursor.close()
    mydb.close()
