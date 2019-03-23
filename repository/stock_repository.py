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
