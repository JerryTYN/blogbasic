import mysql.connector

dataBase = mysql.connector.connect(
    host='localhost',
    user='root',
    password='hoangthi123'
)

cursorObject = dataBase.cursor()

cursorObject.execute("CREATE DATABASE bloght")

print("Complete!")