from apis import *
import datetime
import sqlite3
from db_creator import *
from model import *
from pickle import load

stock = "XBTCZEUR"

# Getting the current price of BTC/USD
def getprice_now():
    try:
        r = requests.get(f'https://finnhub.io/api/v1/crypto/candle?symbol=KRAKEN:{stock}&resolution=1&count=500&token=YOUR-FINNHUB-API-KEY')    
        re = r.json()
        cur_price = re["c"][-1]
        return cur_price
    except:
        print("error")

# Calculating how much BTC we want to buy, now it is at (total_money / 1.1), meaning 90% of your total equity
def volume_calc():
    resp = kraken_request('/0/private/TradeBalance', {
        "nonce": str(int(1000*time.time())),
        "asset": "EUR"
    }, api_key, api_sec)
    js = resp.json()
    total_money = float(js["result"]["eb"])
    moneyperstock = total_money / 1.1
    money_in_eur = getprice_now(stock)
    vol_1 = moneyperstock / float(money_in_eur)
    volume = round(vol_1, 2)
    return (volume)

# Checking if we have an open position because we don't want to buy again if we already have bought
def check_if_bought():
    resp = kraken_request('/0/private/OpenPositions', {
        "nonce": str(int(1000*time.time())),
        "docalcs": True
    }, api_key, api_sec)
    js = resp.json()
    if (js["result"] == {}):
        bought = 0
    else:
        bought = 1
    return bought

# Checking from the Machine Learning model if we should long, short or do nothing
def criteria_check():
    db_creator()
    short_buy, long_buy = train_model()
    if (short_buy):
        telegram_bot_sendtext("Shorter activated")
        buyer_short()
    elif (long_buy):
        telegram_bot_sendtext("Longer activated")
        buyer_long()

# Shorting request to Kraken API
def buyer_short():
    volume = volume_calc()
    now = datetime.now()
    current_time = int(now.strftime("%H%M%S"))
    resp = kraken_request('/0/private/AddOrder', {
        "nonce": str(int(1000*time.time())),
        "userref": current_time,
        "ordertype": "market",
        "type": "sell",
        "volume": volume,
        "pair": stock,
        "leverage": 2
    }, api_key, api_sec)
    volume = round(float(volume), 2)
    telegram_bot_sendtext(f"Shorted {volume} of {stock}")

# Longing request to Kraken API
def buyer_long():
    volume = volume_calc()
    now = datetime.now()
    current_time = int(now.strftime("%H%M%S"))
    resp = kraken_request('/0/private/AddOrder', {
        "nonce": str(int(1000*time.time())),
        "userref": current_time,
        "ordertype": "market",
        "type": "buy",
        "volume": volume,
        "pair": stock,
        "leverage": 2
    }, api_key, api_sec)
    volume = round(float(volume), 2)
    telegram_bot_sendtext(f"Shorted {volume} of {stock}")

# Closing Short position
def sell_short():
    print("Stop-loss activated, buying short order of ETHEUR")
    #Getting volume i.e. how many cryptos I got
    resp = kraken_request('/0/private/OpenPositions', {
        "nonce": str(int(1000*time.time())),
        "docalcs": True
    }, api_key, api_sec)
    js = resp.json()
    js_second = js["result"]
    for k,v in js_second.items():
        volume = js["result"][k]["vol"]
    #Sending buy of short order
    resp = kraken_request('/0/private/AddOrder', {
        "nonce": str(int(1000*time.time())),
        "ordertype": "market",
        "type": "buy",
        "volume": volume,
        "pair": "ETHEUR"
    }, api_key, api_sec)
    js = resp.json()
    print(json.dumps(js, indent=4))
    telegram_bot_sendtext("Seller activated")

# Closing Long position
def sell_long():
    print("Stop-loss activated, buying short order of ETHEUR")
    #Getting volume i.e. how many cryptos I got
    resp = kraken_request('/0/private/OpenPositions', {
        "nonce": str(int(1000*time.time())),
        "docalcs": True
    }, api_key, api_sec)
    js = resp.json()
    js_second = js["result"]
    for k,v in js_second.items():
        volume = js["result"][k]["vol"]
    #Sending buy of short order
    resp = kraken_request('/0/private/AddOrder', {
        "nonce": str(int(1000*time.time())),
        "ordertype": "market",
        "type": "sell",
        "volume": volume,
        "pair": "ETHEUR"
    }, api_key, api_sec)
    js = resp.json()
    print(json.dumps(js, indent=4))
    telegram_bot_sendtext("Seller activated")

# After stop-loss is activated, checking whether to close a long or short pos
def sell():
    resp = kraken_request('/0/private/OpenPositions', {
        "nonce": str(int(1000*time.time())),
        "docalcs": True
    }, api_key, api_sec)
    js = resp.json()
    js_second = js["result"]
    for k,v in js_second.items():
        long_or_short = js["result"][k]["type"]
    if (long_or_short == "buy"):
        sell_long()
    else:
        sell_short()

# Checking for Kraken API whether we have long or short positions open
def long_or_short():
    resp = kraken_request('/0/private/OpenPositions', {
        "nonce": str(int(1000*time.time())),
        "docalcs": True
    }, api_key, api_sec)
    js = resp.json()
    js_second = js["result"]
    for k,v in js_second.items():
        long_or_short = js["result"][k]["type"]
    if (long_or_short == "buy"):
        return (1)
    else:
        return (-1)


# Constantly checking if stop-loss (loss prevention) or profit-target (profit maximizing) has been activated
def sloss_ptarget():
    resp = kraken_request('/0/private/OpenPositions', {
        "nonce": str(int(1000*time.time())),
        "docalcs": True
    }, api_key, api_sec)
    js = resp.json()
    js_second = js["result"]
    for k,v in js_second.items():
        cost = float(js["result"][k]["cost"])
        value = float(js["result"][k]["value"])
    cost_value_ratio = value / cost
    if (long_or_short == 1):
        if (cost_value_ratio < 0.95):
            telegram_bot_sendtext("Stoploss activated")
            sell_long()
        elif (cost_value_ratio > 1.1):
            telegram_bot_sendtext("Profit-target activated")
            sell_long()
    elif (long_or_short == -1):
        if (cost_value_ratio > 1.05):
            telegram_bot_sendtext("Stoploss activated")
            sell_short()
        elif (cost_value_ratio < 0.9):
            telegram_bot_sendtext("Profit-target activated")
            sell_short()

# Main function basically
def tradingbot():
    bought = check_if_bought()
    while True:
        if bought == 1:
            try:
                sloss_ptarget
            except:
                print("error")
            time.sleep(60)
        if bought == 0:
            criteria_check()
            time.sleep(60)

tradingbot()
