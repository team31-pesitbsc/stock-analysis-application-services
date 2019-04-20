import mysql.connector
from common.constants.datasource_constants import HOST, USER_NAME, PASSWORD, DATABASE


def get_companies():
    mydb = mysql.connector.connect(
        host=HOST, user=USER_NAME, passwd=PASSWORD, database=DATABASE)
    mycursor = mydb.cursor()
    query = "SELECT * FROM company ORDER BY SYMBOL"
    mycursor.execute(query)
    data = mycursor.fetchall()
    companies = []
    for row in data:
        companies.append({
            "symbol": row[0],
            "name": row[1],
            "bse_code": row[2]
        })
    mycursor.close()
    mydb.close()
    return companies
