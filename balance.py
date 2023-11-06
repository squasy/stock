import time
from time import timezone

import pyupbit
import datetime
import pytz
access_key = ""
secret_key = ""

upbit = pyupbit.Upbit(access_key, secret_key)
# krw = upbit.get_balance("KRW-ETH")[2]

    #krw = upbit.get_balance()
# ticker="KRW-ETH"
ticker="KRW-BTC"
krw = upbit.get_balance("KRW-AXS")
# print(krw)
orderbook = pyupbit.get_orderbook(ticker)


a1 = upbit.get_balance()
# print(a1)
a2 = round(a1 // 10000)
# print ('a2=',a2)
a3 = a2 * 10000
# print(a3)

# if ticker=="KRW-XRP":
    # print('same')
#print('orderbook = ',orderbook)
sell_price = orderbook['orderbook_units'][0]['bid_price']
# sell_price = orderbook['ask_price'][0]['price']
# print(sell_price)
# unit = krw / float(sell_price)
# unit = 10000 / float(sell_price)
# upbit.buy_market_order(ticker, unit)
# ret = upbit.buy_limit_order(ticker, 100, 50)
# print(ret)
# orderbook = pyupbit.get_orderbook("KRW-ETH")
# print(orderbook)
# now = datetime.datetime.now(pytz.timezone('UTC'))
# mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
# timezone(datetime.timedelta(hours=9))
# print(now)
# print(mid)
now = datetime.datetime.utcnow()
mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
print (now, mid)
# time.sleep(3)
df = pyupbit.get_ohlcv(ticker)
# print(df)
yesterday = df.iloc[-2]
print(yesterday)