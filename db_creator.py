import yfinance as yf
import pandas as pd
import pandas_ta as ta
import sqlite3
import re


# This is for creating DB everytime the program is run, to get the latest data
conn = sqlite3.connect('crypto_database.sqlite')
cur = conn.cursor()
df = yf.Ticker('BTC-USD').history(period='max')[['Close', 'Low', 'High']]

def create_db():
    cur.executescript('''
    DROP TABLE IF EXISTS prices;
    
    CREATE TABLE prices (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        date TEXT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        macd FLOAT,
        macdsig FLOAT,
        macdhis FLOAT,
        rsi FLOAT,
        slowd FLOAT,
        slowk FLOAT,
        target INTEGER
    )''')

    for item in df.itertuples():
        day = re.findall("[^ ]*", str(item[0]))[0]
        close = item[1]
        low = item[2]
        high = item[3]
        cur.execute("INSERT INTO prices (date, high, low, close) VALUES (?, ?, ?, ?)", (day, high, low, close))


def insert_macd():
    macd = df.ta.macd(high = 'High', low = 'Low', close= 'Close')
    for item in macd.itertuples():
        day = re.findall("[^ ]*", str(item[0]))[0]
        macdn = item[1]
        macdhis = item[2]
        macdsig = item[3]
        cur.execute("UPDATE prices set macd = (?), macdhis = (?), macdsig = (?) WHERE date = (?)", (macdn, macdhis, macdsig, day))

def insert_rsi():
    rsi = df.ta.rsi(close= 'Close')
    for item in rsi.iteritems():
        day = re.findall("[^ ]*", str(item[0]))[0]
        rsi = item[1]
        cur.execute("UPDATE prices set rsi = (?) WHERE date = (?)", (rsi, day))

def insert_stoch():
    stoch = df.ta.stoch(high = 'High', low = 'Low', close= 'Close')
    for item in stoch.itertuples():
        day = re.findall("[^ ]*", str(item[0]))[0]
        slowk = item[1]
        slowd = item[2]
        cur.execute("UPDATE prices set slowk = (?), slowd = (?) WHERE date = (?)", (slowk, slowd, day))

def insert_target():
    cur.execute("SELECT close FROM prices")
    pricecur = cur.fetchall()
    prices = []
    for item in pricecur:
        prices.append(item[0])

    id = 0
    i = 0
    sum = []
    for item in prices:
        sum.append(item)
        if i >= 5:
            if (((1 - (sum[0] / sum[5])) * 100) < -10):
                cur.execute("UPDATE prices SET target = 1 WHERE id = (?)", (id,))
            else:
                cur.execute("UPDATE prices SET target = 0 WHERE id = (?)", (id,))
            sum.pop(0)
        i += 1
        id += 1

def db_creator():
    create_db()
    insert_macd()
    insert_rsi()
    insert_stoch()
    insert_target()
    conn.commit()

db_creator()
