import requests, json
import talib
from config import *
import csv
import yfinance as yf
import datetime
from datetime import date

BASE_URL = "https://paper-api.alpaca.markets"

DIRECTORY = "datasets/symbols.csv"

ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDER_URL = "{}/v2/orders".format(BASE_URL)
POSITION_URL = "{}/v2/positions".format(BASE_URL)
ONE_POSITION_URL = "{}/v2/positions/".format(BASE_URL)


HEADERS = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY
}

PROFIT_RATE = 0.15

symbols_500 = []
boughtSymbols = {}

def load_data(dir=DIRECTORY):
    with open(dir) as file:
        data = csv.DictReader(file)
        for x in data:
            symbols_500.append(x['Symbol'])

    r = json.loads(requests.get(POSITION_URL, headers=HEADERS).content)
    for symbol in r:
        boughtSymbols[symbol['symbol']] = symbol['qty']

    print("------Finish Loading ----------")

def get_account():
    r = requests.get(ACCOUNT_URL, headers=HEADERS)
    return json.loads(r.content)

"""
    get current price of a symbol
"""
def get_price(symbol):
    info = yf.Ticker(symbol)
    return info.info["currentPrice"]

def get_bought_price(symbol):
    new_url = "{}/v2/positions/{}".format(BASE_URL, symbol)
    position = json.loads(requests.get(new_url, headers=HEADERS).content)
    return position['avg_entry_price']

def get_bought_qty(symbol):
    new_url = "{}/v2/positions/{}".format(BASE_URL, symbol)
    position = json.loads(requests.get(new_url, headers=HEADERS).content)
    return position['qty']

"""
    Create_order can buy or sell a number of stock
    symbol and qty are straight forward
    side must be a string "buy" or "sell"
    type should be either market, limit, stop, stop_limit or trailing_stop. I usually market so I set it to market by default
    time_in_force should be day, gtc, opg, cls, ioc, fok. I'll set it to "day" by default
"""
def create_order(symbol, qty, side, _type="market", time_in_force="day"):
    data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": _type,
        "time_in_force": time_in_force
    }

    requests.post(ORDER_URL, json=data, headers=HEADERS)

    return None

"""
    This function checks each symbol that this account currently have
    if there is a symbol where we can get a 15% profit, sell it
"""
def shouldSell():
    count = 0
    for symbol in boughtSymbols:
        boughtPrice = get_bought_price(symbol)
        currentPrice = get_price(symbol)
        profit = (currentPrice - boughtPrice) / boughtPrice
        qty = get_bought_qty(symbol)
        if profit >= PROFIT_RATE:
            create_order(symbol, qty, "sell")
            print("Sell {} for price of {} with quantity of {}".format(symbol, currentPrice, qty))
            count += 1
    if count > 0:
        print("Have made {} trades".format(count))
    return None

def current_buying_power():
    response = json.loads(requests.get(ACCOUNT_URL, headers=HEADERS).content)
    return response['buying_power']


"""
    This function checks all the symbols in SP 500
    The buying decision is based on Engulfing
"""
def shouldBuy():
    BUY = 100 #100 dollar
    print("--Deciding which one should buy---")
    today = date.today()
    for symbol in symbols_500:
        data = yf.download(symbol, start="2018-01-01", end=today)
        print("-----checking {} ------".format(symbol))
        try:
            num = talib.CDLENGULFING(data['Open'], data['High'], data['Low'], data['Close'])
        except:
            print("{} has been passed".format(symbol))
            continue
        if num[-1] < 0:
            currentPrice = get_price(symbol)
            qty = BUY // currentPrice
            create_order(symbol, qty, "buy")
            print("Bought {} symbol {} with price of {}".format(qty, symbol, currentPrice))
    return None