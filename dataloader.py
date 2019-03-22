import csv
import requests
import sys

# URL = "http://192.168.2.5:5000/insertStock"
URL = "http://127.0.0.1:5000/insertStock"

symbols = ["INFY"]
for symbol in symbols : 
    with open(symbol+".csv") as f:
        reader = csv.reader(f, delimiter = ',')
        for row in reader:
            data = {
                "Symbol":symbol,
                "Date":row[0],
                "Open":row[1],
                "Close":row[4],
                "High":row[2],
                "Low":row[3],
                "Volume":row[5]
            }
            r = requests.post(url=URL, data=data)
            print(r.text)
            
