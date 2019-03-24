import csv
import requests
import sys

URL = "http://192.168.2.6:5000/stocks"

symbols = ["INFY"]
for symbol in symbols:
    with open("history-data/"+symbol+".csv") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            data = {
                "symbol": symbol,
                "date": row[0],
                "open": row[1],
                "close": row[4],
                "high": row[2],
                "low": row[3],
                "volume": row[5],
                "updatePrediction": False
            }
            r = requests.post(url=URL, data=data)
            print(r.text)
