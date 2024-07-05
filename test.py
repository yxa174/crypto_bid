import requests
session = requests.Session()
price = requests.get('https://api-testnet.bybit.com//v5/market/tickers?category=inverse&symbol=BTCUSD')
print(price.json()['result']['list'][0]['lastPrice'])
