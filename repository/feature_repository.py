import mysql.connector
from common.constants.datasource_constants import HOST, USER_NAME, PASSWORD, DATABASE


def get_features(query_params):
    mydb = mysql.connector.connect(
        host=HOST, user=USER_NAME, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()

    if "limit" in query_params and "offset" in query_params:
        query = 'SELECT * FROM features WHERE `COMPANY_SYMBOL` = %s AND `TRADING_WINDOW` = %s ORDER BY `DATE` ' + \
            query_params['sortDirection']+' LIMIT %s OFFSET %s'
        query_data = (
            query_params['symbol'],
            query_params['tradingWindow'],
            query_params['limit'],
            query_params['offset']
        )
    else:
        query = 'SELECT * FROM features WHERE `COMPANY_SYMBOL` = %s AND `TRADING_WINDOW` = %s ORDER BY `DATE` ' + \
            query_params['sortDirection']
        query_data = (
            query_params['symbol'],
            query_params['tradingWindow'],
        )
    mycursor.execute(query, query_data)
    data = mycursor.fetchall()

    mycursor.close()
    mydb.close()
    return data


def add_feature(feature):
    mydb = mysql.connector.connect(
        host=HOST, user=USER_NAME, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()
    query = "INSERT INTO features VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    query_data = (
        feature["symbol"],
        feature["date"],
        feature['tradingWindow'],
        feature['rsi'],
        feature['K'],
        feature['R'],
        feature['buySell'],
        feature['proc'],
        feature['obv'],
        feature['classLabel'],
        feature['ema12'],
        feature['ema26'],
        feature['ema9macd']
    )
    mycursor.execute(query, query_data)
    mydb.commit()
    mycursor.close()
    mydb.close()
