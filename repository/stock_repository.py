import mysql.connector
from common.constants.datasource_constants import HOST, USER_NAME, PASSWORD, DATABASE
from dateutil import parser


def get_stocks(query_params):
    mydb = mysql.connector.connect(
        host=HOST, user=USER_NAME, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()

    query = "SELECT * FROM stock WHERE `COMPANY_SYMBOL` = %s ORDER BY `DATE` DESC LIMIT %s OFFSET %s"
    query_data = (
        query_params['symbol'],
        query_params['limit'],
        query_params['offset']
    )
    mycursor.execute(query, query_data)
    data = mycursor.fetchall()

    response = {
        "companySymbol": query_params['symbol'],
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


def add_stock(request):
    mydb = mysql.connector.connect(
        host=HOST, user=USER_NAME, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()
    query = "INSERT INTO stock VALUES (%s, %s, %s, %s, %s, %s, %s)"
    query_data = (
        request.form.get("symbol"),
        request.form.get("date"),
        request.form.get("open"),
        request.form.get("close"),
        request.form.get("high"),
        request.form.get("low"),
        request.form.get("volume"),
    )
    mycursor.execute(query, query_data)
    mydb.commit()
    mycursor.close()
    mydb.close()


def update_stock(request):
    mydb = mysql.connector.connect(
        host=HOST, user=USER_NAME, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()

    query = "UPDATE stock SET `OPEN`=%s, `CLOSE` = %s, `HIGH` = %s, `LOW` = %s, `VOLUME` = %s WHERE `COMPANY_SYMBOL` = %s AND `DATE` = %s"
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
