'''
title: db functions
author: Stephanie Leung
date-created: 2022-01-20
'''
import sqlite3
import json
from urllib.request import urlopen
from api_key import API_KEY

# --- Variables --- #
DB_NAME = "stock_tracker.db"


# --- Functions -- - #
# --- Setup
def createTables():
    '''
    creates tables in database
    :return: (None)
    '''
    global DB_NAME
    CONNECTION = sqlite3.connect(DB_NAME)
    CURSOR = CONNECTION.cursor()
    CURSOR.execute('''
        CREATE TABLE
            user_info (
                username TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            );
    ''')
    CURSOR.execute('''
        CREATE TABLE
            stock_portfolio (
                username TEXT,
                ticker TEXT,
                purchase_price REAL,
                shares REAL,
                PRIMARY KEY(username, ticker)
            );
    ''')
    CONNECTION.commit()
    CONNECTION.close()


# --- Login Information
# -- Inputs
def addAccount(USERNAME, EMAIL, PASSWORD):
    '''
    adds new user info to database
    :param USERNAME: (str)
    :param EMAIL: (str)
    :param PASSWORD: (str)
    :return: (None)
    '''
    global DB_NAME
    CONNECTION = sqlite3.connect(DB_NAME)
    CURSOR = CONNECTION.cursor()
    CURSOR.execute('''
        INSERT INTO
            user_info
        VALUES (
            ?,?,?
        );
    ''', [USERNAME, EMAIL, PASSWORD])
    CONNECTION.commit()
    CONNECTION.close()


# -- Processing
def validateLogin(USERNAME, PASSWORD):
    '''
    checks if email and password matches
    :param USERNAME: (str)
    :param PASSWORD: (str)
    :return: (bool)
    '''
    global DB_NAME
    CONNECTION = sqlite3.connect(DB_NAME)
    CURSOR = CONNECTION.cursor()
    DB_PASSWORD = CURSOR.execute('''
        SELECT
            password
        FROM
            user_info
        WHERE
            username = ?;
    ''', [USERNAME, ]).fetchone()
    if DB_PASSWORD is None:
        USERNAME = USERNAME.lower()
        DB_PASSWORD = CURSOR.execute('''
            SELECT
                password
            FROM
                user_info
            WHERE
                email = ?;     
        ''', [USERNAME, ]).fetchone()
    CONNECTION.close()
    if DB_PASSWORD is None:
        return False
    elif PASSWORD == DB_PASSWORD[0]:
        return True
    else:
        return False


def getAccount(EMAIL, USERNAME):
    '''
    checks if an account with the existing email/username exists
    :param EMAIL: (str)
    :param USERNAME: (str)
    :return: (bool)
    '''
    global DB_NAME
    CONNECTION = sqlite3.connect(DB_NAME)
    CURSOR = CONNECTION.cursor()
    SEARCH_EMAIL = CURSOR.execute('''
        SELECT
            *
        FROM
            user_info
        WHERE
            email = ?;
    ''', [EMAIL, ]).fetchone()
    SEARCH_USERNAME = CURSOR.execute('''
        SELECT 
            *
        FROM
            user_info
        WHERE
            username = ?;
    ''', [USERNAME, ]).fetchone()
    CONNECTION.close()
    if SEARCH_EMAIL or SEARCH_USERNAME:
        return True
    else:
        return False


def getUsername(EMAIL):
    '''
    gets the username associated with email
    :param EMAIL: (str)
    :return: (str)
    '''
    global DB_NAME
    CONNECTION = sqlite3.connect(DB_NAME)
    CURSOR = CONNECTION.cursor()
    USERNAME = CURSOR.execute('''
        SELECT
            username
        FROM
            user_info
        WHERE
            email = ?;
    ''', [EMAIL, ]).fetchone()
    CONNECTION.close()
    if USERNAME:
        return USERNAME[0]
    else:
        return EMAIL


# --- Stock Portfolio Information
# -- Inputs
def addStockInfo(USERNAME, TICKER, PURCHASE_PRICE, SHARES):
    '''
    adds new stock information to database
    :param USERNAME: (str)
    :param TICKER: (str)
    :param PURCHASE_PRICE: (float)
    :param SHARES: (float)
    :return: (None)
    '''
    global DB_NAME
    CONNECTION = sqlite3.connect(DB_NAME)
    CURSOR = CONNECTION.cursor()
    CURSOR.execute('''
        INSERT INTO
            stock_portfolio
        VALUES (
            ?,?,?,?
        );
    ''', [USERNAME, TICKER, PURCHASE_PRICE, SHARES])
    CONNECTION.commit()
    CONNECTION.close()


def updateStockInfo(USERNAME, SYMBOL, SHARES):
    '''
    edits existing stock information
    :param USERNAME: (str)
    :param SYMBOL: (str)
    :param SHARES: (float)
    :return: (None)
    '''
    global DB_NAME
    CONNECTION = sqlite3.connect(DB_NAME)
    CURSOR = CONNECTION.cursor()
    CURSOR.execute('''
        UPDATE
            stock_portfolio
        SET
            shares = ?
        WHERE
            username = ?
            AND 
            ticker = ?;
    ''', [SHARES, USERNAME, SYMBOL])
    CONNECTION.commit()
    CONNECTION.close()


# -- Processing
def checkTicker(USERNAME, SYMBOL):
    '''
    checks if symbol matches with existing tickers in portfolio
    :param USERNAME: (str)
    :return: (bool)
    '''
    global DB_NAME
    CONNECTION = sqlite3.connect(DB_NAME)
    CURSOR = CONNECTION.cursor()
    SYMBOLS = CURSOR.execute('''
        SELECT
            ticker
        FROM
            stock_portfolio
        WHERE
            username = ?;
    ''', [USERNAME, ]).fetchall()
    CONNECTION.close()

    for symbol in SYMBOLS:
        if SYMBOL == symbol[0]:
            return True
    return False


def deleteStockInfo(USERNAME, SYMBOL):
    '''
    deletes stock info for user
    :param USERNAME: (str)
    :param SYMBOL: (str)
    :return: (None)
    '''
    global DB_NAME
    CONNECTION = sqlite3.connect(DB_NAME)
    CURSOR = CONNECTION.cursor()
    CURSOR.execute('''
        DELETE FROM
            stock_portfolio
        WHERE
            username = ?
            AND 
            ticker = ?;
    ''', [USERNAME, SYMBOL])
    CONNECTION.commit()
    CONNECTION.close()


def calculateChange(STOCK_INFO):
    '''
    calculates change in cost
    :param STOCK_INFO: (list)
    :return: (float)
    '''
    CHANGE = (STOCK_INFO[1] - STOCK_INFO[2]) * STOCK_INFO[3]
    return CHANGE


def findTickerInformation(STOCK):
    '''
    calls API to find stock price of given symbol
    :param SYMBOL: (list)
    :return: (list)
    '''
    global API_KEY
    URL = f"https://financialmodelingprep.com/api/v3/quote-short/{STOCK[0]}?apikey={API_KEY}"
    DATA = urlopen(URL)
    DATA = DATA.read().decode("utf-8")
    DATA = json.loads(DATA)
    STOCK.append(round(DATA[0]['price'], 2))
    return STOCK


# -- Outputs
def tickerInformation(USERNAME):
    '''
    finds all ticker symbols and price that user is tracking
    :param USERNAME: (str)
    :return: (list) 2d-array
    '''
    global DB_NAME
    global API_KEY
    CONNECTION = sqlite3.connect(DB_NAME)
    CURSOR = CONNECTION.cursor()
    SYMBOLS = CURSOR.execute('''
        SELECT
            ticker, purchase_price, shares
        FROM
            stock_portfolio
        WHERE
            username = ?;
    ''', [USERNAME, ]).fetchall()
    CONNECTION.close()

    STOCKS = []
    for i in range(len(SYMBOLS)):
        STOCKS.append([SYMBOLS[i][0], ])
        STOCKS[i] = findTickerInformation(STOCKS[i])
        STOCKS[i] += [SYMBOLS[i][1], SYMBOLS[i][2]]

    return STOCKS
