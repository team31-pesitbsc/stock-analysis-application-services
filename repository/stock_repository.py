import mysql.connector
from common.constants.datasource_constants import HOST, USER_NAME, PASSWORD, DATABASE
from dateutil import parser


def get_stocks(request):
    mydb = mysql.connector.connect(
        host=HOST, user=USER_NAME, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()

    query = "SELECT * FROM stock WHERE Stock_symbol = %s ORDER BY Stock_date DESC LIMIT %s OFFSET %s"
    query_data = (
        request.args['symbol'],
        int(request.args['limit']),
        int(request.args['offset'])
    )
    mycursor.execute(query, query_data)
    data = mycursor.fetchall()

    response = {
        "companySymbol": request.args['symbol'],
        "stocks": []
    }
    for row in data:
        response['stocks'].append({
            "date": row[1],
            "open": row[2],
            "close": row[3],
            "high": row[4],
            "low": row[5],
            "volume": row[6],
        })

    mycursor.close()
    mydb.close()
    return response


def update_stock(request):
    mydb = mysql.connector.connect(
        host=HOST, user=USER_NAME, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()

    query = "UPDATE stock SET Stock_open=%s, Stock_close = %s, Stock_high = %s, Stock_low = %s, Stock_volume = %s WHERE Stock_symbol = %s AND Stock_date = %s"
    query_data = (
        request.form.get("open"),
        request.form.get("close"),
        request.form.get("high"),
        request.form.get("low"),
        request.form.get("volume"),
        request.form.get("symbol"),
        request.form.get("date")
    )
    mycursor.execute(query, query_data)
    mydb.commit()

    mycursor.close()
    mydb.close()
