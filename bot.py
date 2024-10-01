# The above code is importing the necessary libraries for the program to run.
import webbrowser
import selenium
import requests
import time
import json
from selenium import webdriver


from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


import random
from hashlib import sha256

from datetime import datetime

from databaseCreation import mycursor, myDatabase


def signUp(mycursor):
    """
    It asks the user if they want to sign up or login, if they want to sign up it asks for their email,
    generates a key, sends the key to the email, and then adds the email and key to the database. If
    they want to login, it asks for their key and checks if it exists in the database
    
    """
    loggedIn = False
    while loggedIn==False:
        signedUp = input("Would you like to sign up or login? (S/L) ")
        
        if signedUp == "S" or signedUp == "s":
            email = input("Please enter your email where you want to receive your key: ")
            key = generateKey()
            sendEmail(key, email)
            mycursor.execute("INSERT INTO myDatabase.users (email, userKey) VALUES (%s, %s);",(email, sha256(key.encode('utf-8')).hexdigest()))
            myDatabase.commit()
            loggedIn = True
        
        elif signedUp == "L" or signedUp == "l":
            key = input("Please enter your key ")
            sql = "SELECT EXISTS(SELECT * FROM users WHERE userKey=%s)"
            val = (sha256(key.encode('utf-8')).hexdigest(),)
            mycursor.execute(sql, val)
            result = mycursor.fetchall()
            if result[0][0] == 1:
                loggedIn = True
            else:
                print("That key does not exist")
                loggedIn = False

    return key

def getUserID(mycursor, userKey):
    """
    This function takes in a userKey and returns the userID associated with that userKey
    
    :param mycursor: the cursor object
    :param userKey: The user's unique key
    :return: The userID of the userKey that is passed in.
    """
    sql = "SELECT userID FROM users WHERE userKey=%s"
    val = (userKey,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    userID = result[0]
    return userID


# should work - generates a key when the user signs up 4.5/5 ---- 15:43 26/01


def generateKey():
    """
    It generates a random string of 25 characters, separated into 5 chunks of 4 characters each, with a
    dash in between each chunk
    :return: A string of 25 characters, with a dash every 4 characters.
    """
    key = ''
    chunk = ''
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    for i in range(5):
        key = ''
        while len(key) < 25:
            char = random.choice(alphabet)
            key += char
            chunk += char
            if len(chunk) == 4:
                key += '-'
                chunk = ''
        key = key[:-1]
    return key


# should work - sends an email to the user with their key. API use 4.5/5 ----- 15:43 26/01
def sendEmail(key, email):
    """
    It sends an email to the email address provided with the key provided
    
    :param key: The key that you want to send to the user
    :param email: The email address of the recipient
    """
    url = "https://rapidprod-sendgrid-v1.p.rapidapi.com/mail/send"
    payload = {
        "personalizations": [
            {
                "to": [{"email": email}],
                "subject": "Here is your key to brendons bot"
            }
        ],
        "from": {"email": "brendonsbot@test.com"},
        "content": [
            {
                "type": "text/plain",
                "value": key
            }
        ]
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "ac2968f349msh267cd43ba2b2c06p1009d2jsnc328c504077d",
        "X-RapidAPI-Host": "rapidprod-sendgrid-v1.p.rapidapi.com"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)

##### MENU



##### USER SETS ADDRESSES AND ADDED TO DATABASE


def setAddress(mycursor, myDatabase):
    """
    This function allows the user to input their address details and then saves them to the database.
    """
    
    firstName = input("Please enter the addresses first name: ")
    lastName = input("Please enter the addresses last name: ")
    email = input("Please enter the addresses email: ")
    addressOne = input("Please enter the first line of the address: ")
    addressTwo = input("Please enter the second line of the address(if needed): ")
    city = input("Please enter the addresses city: ")
    postcode = input("Please enter the addresses postcode: ")
    country = input("Please enter the addresses country: ")
    phoneNum = input("Please enter the addresses phone number: ")
    userID = 2
    log = "INSERT INTO myDatabase.address VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    val = (firstName, lastName, email, addressOne, addressTwo, city, postcode, country, phoneNum, userID)
    mycursor.execute(log, val)
    myDatabase.commit()
    print("Address saved")

def setBilling(mycursor, myDatabase):
    """
    It takes in the user's billing information and saves it to the database
    """
    nameOnCard = input("Please enter name on card: ")
    cardNumber = input("Please enter card number: ")
    expiryMonth = input("Please enter expiry month(2 numbers e.g. 09): ")
    expiryYear = input("Please enter expiry year(last 2 number e.g. 2024 -> 24): ")
    cvv = input("Please enter the cvv")
    userID = 2
    log = "INSERT INTO myDatabase.billing VALUES (%s, %s, %s, %s, %s, %s);"
    val = (nameOnCard, cardNumber, expiryMonth, expiryYear, cvv, userID)
    mycursor.execute(log, val)
    myDatabase.commit()
    print("Billing saved")



def getProducts():
    """
    It takes the JSON data from the Palace website, and returns a dictionary with the product name as
    the key, and a tuple of the product handle and price as the value.
    :return: A dictionary with the product name as the key and a tuple of the handle and price as the
    value.
    """

    r = requests.get('https://shop.palaceskateboards.com/products.json')
    products = json.loads(r.text)['products']

    productNameHandlePrice = {}

    for product in products:
        productName = product['title']
        handle = product['handle']
        price = product['variants'][0]['price']
        productNameHandlePrice[productName] = (handle, price)

    return productNameHandlePrice


##### selenium stuff


def getWant():
    """
    It asks the user for the name of the product they want to purchase, and if they don't know the name,
    it tells them how to find it.
    :return: the name of the product that the user wants to purchase.
    """
    want = input(
        "Enter exact name of product you want to purchase. If you do not know the exact name please input N: ")

    if want == "N" or want == "n":
        print("To get the name of the item you want please go to https://www.palaceskateboards.com/range/ultimo-2022/ , find the item you want, and copy the first line that contains the name of the item and the colour at the end (e.g. P-3B BAFFLE PARKA OLIVE) ")
        print("Remember to check if the item you want it coming out this week. One source is maxmerch on instagram, who will also show prices and the titles of the products that are coming out")
        want = input(
            "After you've checked, please enter the exact name of the product you want to purchase: ")
    else:
        want = want.upper()

    return want

def getSize():
    """
    It takes a user input, and if the input is one of the following: "OS", "S", "M", "L", "XL", it
    returns the corresponding string
    :return: The size of the item the user wants to buy.
    """

    size = input(
        "Please enter the size of the item you want to buy (OS - for accessories, S, M, L, XL):")

    if size.upper() == "OS":
        size = "One Size"
    elif size.upper() == "S":
        size = "Small"
    elif size.upper() == "M":
        size = "Medium"
    elif size.upper() == "L":
        size = "Large"
    elif size.upper() == "XL":
        size = "X-Large"
    else:
        print("not a valid input")

    return size 


def findProduct(want, productNameHandlePrice): 
    if want in productNameHandlePrice:
        print("Product found")
        return productNameHandlePrice[want][0]
    else:
        print("Product not found")


    #when doing cartProduct(findProduct(), size)
def cartProduct(id, size, driver):
    """
    It takes the product ID and size as parameters, navigates to the product page, selects the size, and
    adds the product to the cart
    
    :param id: the id of the product you want to add to cart
    :param size: the size of the item you want to buy
    """
    
    driver.get("https://shop.palaceskateboards.com/products/" + id)

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "product-select"))) 

    time.sleep(3)

    sizeMenu = Select(driver.find_element(By.ID, 'product-select'))

    sizeMenu.select_by_visible_text(size)  

    (driver.find_element(By.NAME, 'button')).click()

    time.sleep(3)



def agreeTC(driver):
    """
    It clicks the checkbox to agree to the terms and conditions, then clicks the checkout button.
    """

    driver.get("https://shop.palaceskateboards.com/cart")

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "checkbox-control")))

    (driver.find_element(By.CLASS_NAME, 'checkbox-control')).click()

    time.sleep(0.1)

    (driver.find_element(By.ID, 'checkout')).click()




def shippingInfo(driver, mycursor):
    """
    This function is used to fill in the shipping information form on the checkout page. Variables are assigned the IDs of text fields at checkout.
    The function then fills the text fields with the user's information that is pulled from the database.
    """
    wait = WebDriverWait(driver, 5)
    desiredUrl = "https://shop.palaceskateboards.com/throttle/queue"
    wait.until(EC.url_changes(desiredUrl))

    #(driver.find_element(By.ID, 'continue-button')).click()

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "checkout_shipping_address_first_name")))

    
    email = driver.find_element(By.ID, 'checkout_email')
    firstName = driver.find_element(By.ID, 'checkout_shipping_address_first_name')
    lastName = driver.find_element(By.ID, "checkout_shipping_address_last_name")
    addressOne = driver.find_element(By.ID,"checkout_shipping_address_address1")
    city = driver.find_element(By.ID, "checkout_shipping_address_city")
    postcode = driver.find_element(By.ID, "checkout_shipping_address_zip")
    country = driver.find_element(By.ID, "checkout_shipping_address_country")
    phoneNum = driver.find_element(By.ID, "checkout_shipping_address_phone")

    mycursor.execute('SELECT address.email FROM address INNER JOIN users ON address.userID = users.userID WHERE address.userID = 2;')
    email.send_keys((mycursor.fetchone())[0])

    mycursor.execute('SELECT address.firstName FROM address INNER JOIN users ON address.userID = users.userID WHERE address.userID = 2;')
    firstName.send_keys((mycursor.fetchone())[0])

    mycursor.execute('SELECT address.lastName FROM address INNER JOIN users ON address.userID = users.userID WHERE address.userID = 2;')
    lastName.send_keys((mycursor.fetchone())[0])

    mycursor.execute('SELECT address.addressOne FROM address INNER JOIN users ON address.userID = users.userID WHERE address.userID = 2;')
    addressOne.send_keys((mycursor.fetchone())[0])

    mycursor.execute('SELECT address.city FROM address INNER JOIN users ON address.userID = users.userID WHERE address.userID = 2;')
    city.send_keys((mycursor.fetchone())[0])

    mycursor.execute('SELECT address.postcode FROM address INNER JOIN users ON address.userID = users.userID WHERE address.userID = 2;')
    postcode.send_keys((mycursor.fetchone())[0])

    mycursor.execute('SELECT address.country FROM address INNER JOIN users ON address.userID = users.userID WHERE address.userID = 2;')
    country.send_keys((mycursor.fetchone())[0])

    mycursor.execute('SELECT address.phoneNum FROM address INNER JOIN users ON address.userID = users.userID WHERE address.userID = 2;')
    phoneNum.send_keys((mycursor.fetchone())[0])



    time.sleep(3)

    (driver.find_element(By.XPATH,'/html/body/div/div[2]/div/div[2]/div[2]/form/div[2]/button')).click() 




def billingInfo(driver, mycursor):
    """
    It takes the billing information from the database and inputs it into the billing information form. Variables are assigned the IDs of text fields at checkout.
    The function then fills the text fields with the user's information that is pulled from the database.
    """

    (driver.find_element(By.NAME, 'button')).click()

    

    time.sleep(5)
    
    driver.switch_to.frame(driver.find_element(By.CLASS_NAME, 'card-fields-iframe'))
    iframe = driver.find_element(By.XPATH, '/html/body/form/input[1]')


    mycursor.execute('SELECT billing.cardNumber FROM billing INNER JOIN users ON billing.userID = users.userID WHERE billing.userID = 2;')
    cardNumber = (mycursor.fetchone())[0]

    mycursor.execute('SELECT billing.nameOnCard FROM billing INNER JOIN users ON billing.userID = users.userID WHERE billing.userID = 2;')
    nameOnCard = (mycursor.fetchone())[0]

    mycursor.execute('SELECT CONCAT(billing.expiryMonth,billing.expiryYear) FROM billing INNER JOIN users ON billing.userID = users.userID WHERE billing.userID = 2;')
    expiry = (mycursor.fetchone())[0]

    mycursor.execute('SELECT billing.cvv FROM billing INNER JOIN users ON billing.userID = users.userID WHERE billing.userID = 2;')
    cvv = (mycursor.fetchone())[0]
    
    iframe.send_keys(cardNumber, Keys.TAB, Keys.TAB, nameOnCard, Keys.TAB, expiry, Keys.TAB, cvv)

    

    time.sleep(1)
    
    driver.switch_to.default_content()

    time.sleep(1) 


    (driver.find_element(By.NAME,'button')).click() 

    


def logPurchase(want, productNameHandlePrice):
    """
    It takes the name of the product you want to buy, and the dictionary of products, and then it saves
    the purchase to the database
    
    :param want: The product name
    :param productNameHandlePrice: A dictionary of dictionaries. The first dictionary is the product
    name, the second dictionary is the product handle and price
    """

    log = "INSERT INTO myDatabase.purchases (store, product, price, purchaseDate) VALUES (%s, %s, %s, %s);"
    val = ("Palace Skateboards", want, productNameHandlePrice[want][1], datetime.now().strftime("%H:%M:%S %d/%m/%Y"))
    mycursor.execute(log, val)
    myDatabase.commit()
    print("Purchase saved")




def program(mycursor):
    """
    The program is finally ran
    """
    #key = 
    signUp(mycursor)
    #userID = getUserID(mycursor, key)
    
    options = webdriver.ChromeOptions()
    options.add_argument('disable-infobars')
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    
    
    while True:
        print()
        print("a = addresses")
        print("b = billing info")
        print("t = tasks")
        print("x = exit")
        print()

        userInput = input("Enter an option:")

        if userInput == "a" or userInput == "A":
            setAddress(mycursor, myDatabase)

        elif userInput == "b" or userInput == "B":
            setBilling(mycursor, myDatabase)

        elif userInput == "t" or userInput == "T":
            
            print(getProducts())

            cartProduct(findProduct(getWant(), getProducts()), getSize(), driver)
            agreeTC(driver)
            shippingInfo(driver, mycursor)
            billingInfo(driver, mycursor)
            logPurchase(getWant(), getProducts())

        elif userInput == "x" or userInput == "X":
            quit()
        else:
            print("Not a valid option")
        

program(mycursor)