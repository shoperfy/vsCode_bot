import mysql.connector

myDatabase = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database='myDatabase'
)

mycursor = myDatabase.cursor()


####  create it not exists so it dont make tables agane i hope ---- wanna make diff tables for every user tbh
def makeDatabase(mycursor, myDatabase):
    mycursor.execute("CREATE DATABASE IF NOT EXISTS myDatabase;")
    myDatabase.commit()
    mycursor.execute("CREATE TABLE IF NOT EXISTS myDatabase.users(userId INT PRIMARY KEY AUTO_INCREMENT, email VARCHAR(320), userKey VARCHAR(100));")
    myDatabase.commit()
    mycursor.execute("CREATE TABLE IF NOT EXISTS myDatabase.address(firstName VARCHAR(255), lastName VARCHAR(255), email VARCHAR(255), addressOne VARCHAR(255), addressTwo VARCHAR(255), city VARCHAR(255), postcode VARCHAR(255), country VARCHAR(255), phoneNum VARCHAR(255), userId VARCHAR(255));")
    myDatabase.commit()
    mycursor.execute("CREATE TABLE IF NOT EXISTS myDatabase.billing(nameOnCard VARCHAR(255), cardNumber VARCHAR(255), expiryMonth VARCHAR(2), expiryYear VARCHAR(2), cvv VARCHAR(3), userId VARCHAR(255))")
    myDatabase.commit()
    mycursor.execute(
        "CREATE TABLE IF NOT EXISTS myDatabase.purchases(store VARCHAR(255), product VARCHAR(255), price VARCHAR(255), purchaseDate VARCHAR(255), userId VARCHAR(255));")


