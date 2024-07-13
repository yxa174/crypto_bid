import requests
import time
import sqlite3
import os
# import pdb; pdb.set_trace()


def get_info():
    response = requests.get(url="https://yobit.net/api/3/info")

    with open("info.txt", "w") as file:
        file.write(response.text)

    return response.text


def get_ticker(coin1="btc", coin2="usd"):
    # response = requests.get(url="https://yobit.net/api/3/ticker/eth_btc-xrp_btccc?ignore_invalid=1")
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

    # info = f"[-] TOTAL {coin1} SELL: {round(total_trade_ask, 2)} $\n[+] TOTAL {coin1} BUY: {round(total_trade_bid, 2)} $"
    
    info = [round(total_trade_ask), round(total_trade_bid, 2)]

    return info
def price(coin1="BTC", coin2="USD"):
    session = requests.Session()
    # get_price = requests.get(url=f"https://yobit.net/api/3/ticker/{coin1}_{coin2}?ignore_invalid=1")
    # sss = get_price.json()[f'{coin1}_{coin2}']['sell']
    get_price = session.get(f'https://api-testnet.bybit.com//v5/market/tickers?category=inverse&symbol={coin1}{coin2}')
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
def main():
    balance = 10000
    minus = 1000
    lot = 1.0
    sall_ = 1.0  
    while True:
        try: 
            time.sleep(1)
            one_trades = get_trades(coin1="btc")
            current_price = price(coin1='BTC')

            os.system('cls' if os.name == 'nt' else 'clear')
            
            print(f'Продажи: {one_trades[0]} $')
            print(f'Покупки: {one_trades[1]} $')
            # print(one_trades[12:-9])
            if one_trades[1] > one_trades[0]*1.1:
                print("\033[92mПокупать!\033[0m")
            else:
                print("\033[91mПродавать!\033[0m")

            print(f'balance: {round(balance, 2)} $')
            print(f'куплено за: {lot}')
            print('продано за:', sall_)
            
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
            
            if balance >= 10000 and one_trades[1] > one_trades[0]*1.1:
                balance = balance - minus
                lot = float(current_price[:8]) 
                
                    # breakpoint()
                # if lot + lot/10000 > (float(current_price[:8]) + (float(current_price[:8]) / 10000)): #рабочая 
                if (float(current_price[:8])) > lot + lot/10000:
                    # sall_ = lot + round(lot / 10000, 2)
                    sall_ = float(current_price[:8])
                    balance = balance + (minus + round(minus / 10000, 2))
                    # lot = 0.0
                    # sall_ = 0.0
                else:
                    pass
        except ZeroDivisionError:
            # Do nothing if ZeroDivisionError occurs
            pass
if __name__ == '__main__':
    main()
    # hello 
    
