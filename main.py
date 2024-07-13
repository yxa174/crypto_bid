import requests
import time
import sqlite3
import os
from collections import deque

def get_info():
    response = requests.get(url="https://yobit.net/api/3/info")

    with open("info.txt", "w") as file:
        file.write(response.text)

    return response.text


def get_ticker(coin1="btc", coin2="usd"):
    response = requests.get(url=f"https://yobit.net/api/3/ticker/{coin1}_{coin2}?ignore_invalid=1")
    with open("ticker.txt", "w") as file:
        file.write(response.text)
    return response.text


def get_depth(coin1="btc", coin2="usd", limit=150):
    response = requests.get(url=f"https://yobit.net/api/3/depth/{coin1}_{coin2}?limit={limit}&ignore_invalid=1")
    with open("depth.txt", "w") as file:
        file.write(response.text)
    bids = response.json()[f"{coin1}_usd"]["bids"]
    total_bids_amount = 0
    for item in bids:
        price = item[0]
        coin_amount = item[1]
        total_bids_amount += price * coin_amount
    return f"Total bids: {total_bids_amount} $"


def get_trades(coin1="btc", coin2="usd", limit=150):
    response = requests.get(url=f"https://yobit.net/api/3/trades/{coin1}_{coin2}?limit={limit}&ignore_invalid=1")
    with open("trades.txt", "w") as file:
        file.write(response.text)
    total_trade_ask = 0
    total_trade_bid = 0
    for item in response.json()[f"{coin1}_{coin2}"]:
        if item["type"] == "ask":
            total_trade_ask += item["price"] * item["amount"]
        else:
            total_trade_bid += item["price"] * item["amount"]
    info = [round(total_trade_ask), round(total_trade_bid, 2)]
    return info

def price(coin1="btc", coin2="usd"):
    session = requests.Session()
    get_price = session.get(f'https://api-testnet.bybit.com//v5/market/tickers?category=inverse&symbol={coin1.upper()}{coin2.upper()}')
    sss = get_price.json()['result']['list'][0]['lastPrice']
    return sss


# def main():
#     while True:
#         time.sleep(0.1)
#         # print(get_info())
#         # print(get_ticker())
#         # print(get_ticker(coin1="eth"))
#         # print(get_depth())
#         # print(get_depth(coin1="doge"))
#         # print(get_depth(coin1="doge", limit=2000))
#         # print(get_trades())
#         print(get_trades(coin1="xrp"))
#         print(get_trades(coin1="doge"))

# Establish a connection to the SQLite database
conn = sqlite3.connect('price_data.db')
cursor = conn.cursor()

# Create a table to store price data if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY,
                    price REAL
                )''')


def get_previous_price():
    cursor.execute('DELETE FROM price_history WHERE rowid NOT IN (SELECT rowid FROM price_history ORDER BY rowid DESC LIMIT 2);')
    cursor.execute('SELECT price FROM price_history ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return None

def check_price_jump(depth, threshold=10):
    if len(prices) < 5:
        return False, 0
    min_price = min(prices)
    max_price = max(prices)
    percent_jump = ((max_price - min_price) / min_price) * 100
    return percent_jump > threshold, percent_jump
prices = deque(maxlen=5)

def main():
    balance = 10000
    minus = 1000
    lot = 0.0
    sall_ = 0.0  
    persent = 10000 
    while True:
        try:
            coin1 = 'btc'
            depth = get_depth(coin1)[12:22]
            current_price_depth = depth
            prices.append(current_price_depth)
            time.sleep(1)
            one_trades = get_trades(coin1)
            current_price = price(coin1)
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"Текущая цена: {current_price_depth}")
            print(f'Продажи: {one_trades[0]} $')
            print(f'Покупки: {one_trades[1]} $')
            if one_trades[1] > one_trades[0]*1.2: #Уведомление о ПОКУПАТЬ или ПРОДАВАТЬ
                print("\033[92mПокупать!\033[0m")
            else:
                print("\033[91mПродавать!\033[0m")

            print(f'balance: {round(balance, 2)} $')
            print(f'куплено за: {lot}')
            print('продано за:', sall_)
            cursor.execute('DELETE FROM buy_sell WHERE rowid NOT IN (SELECT rowid FROM buy_sell ORDER BY rowid DESC LIMIT 10);')
            cursor.execute('INSERT OR IGNORE INTO buy_sell (sell) VALUES (?)', (one_trades[1],))
            cursor.execute('INSERT OR IGNORE INTO buy_sell (buy) VALUES (?)', (one_trades[0],))
            conn.commit()           
            previous_price = get_previous_price()
            if previous_price is not None:
                if previous_price > float(current_price):
                    arrow = "\033[91m↓\033[0m"  # Arrow pointing down
                else:
                    arrow = "\033[92m↑\033[0m"  # Arrow pointing up
            else:
                arrow = ""

            s = f"{current_price}{arrow}"
            print(s)

            # Insert the current price into the price_history table
            cursor.execute('INSERT INTO price_history (price) VALUES (?)', (current_price,))
            conn.commit()
            
            if balance >= persent and one_trades[1] > one_trades[0]*1.2: #Сравнение покупать или не покупать
                balance = balance - minus
                lot = float(current_price[:8]) 
                
                    # breakpoint()
            if lot + lot/persent < (float(current_price[:8])) and balance < 10000: # + (float(current_price[:8]) / persent)): #рабочая 
            # if (float(current_price[:8])) > lot + lot/10000:
                sall_ = lot + round(lot / persent, 2)
                # sall_ = float(current_price[:8])
                balance = balance + (minus + round(minus / persent, 2))
                # lot = 0.0
                # sall_ = 0.0
            else:
                pass
        except Exception:
           pass # игнорировать все ошибки 
if __name__ == '__main__':
    main()
