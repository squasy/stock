import time
import pyupbit
import datetime

con_key = ""
sec_key = ""

upbit = pyupbit.Upbit(con_key, sec_key)
# ticker="KRW-ETH"
mTicker="KRW-BTC"
def get_target_price(ticker):
    buy_status = 0
    df = pyupbit.get_ohlcv(ticker)
    yesterday = df.iloc[-2]

    today_open = yesterday['close']
    yesterday_high = yesterday['high']
    yesterday_low = yesterday['low']
    # print(today_open, yesterday_high-yesterday_low)
    target = today_open + (yesterday_high - yesterday_low) * 0.5
    return target

def sell_crypto_currency(ticker):
    global buy_status
    buy_status=0
    unit = upbit.get_balance(ticker)
    # print(unit)
    if unit==0:
        return
    upbit.sell_market_order(ticker, unit)
    time.sleep(1)
    print('sell success')

def get_yesterday_ma5(ticker):
    df = pyupbit.get_ohlcv(ticker)
    close = df['close']
    ma = close.rolling(window=5).mean()
    return ma[-2]

now = datetime.datetime.utcnow()
mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
ma5 = get_yesterday_ma5(mTicker)
target_price = get_target_price(mTicker)
# print(mid)
# print(mid + datetime.timedelta(seconds=10))
buy_status = 0


def buy_crypto_currency(ticker, cur_price):
    global buy_status
    # print(buy_status)
    if buy_status==1:
        return
    # print(ticker)
    balance = upbit.get_balance()
    # print(balance)
    krw =balance*0.95
    # print(krw)
    # orderbook = pyupbit.get_orderbook(ticker)
    # sell_price = orderbook['asks'][0]['price']
    unit = round(krw / float(cur_price),8)
    # unit = "{:3f}".format(round(krw / float(cur_price),10))
    # strUnit = 'unit='+ unit
    print(krw, unit)
    # upbit.buy_limit_order(ticker, cur_price,  unit)
    upbit.buy_market_order(ticker, cur_price, unit)
    time.sleep(5)
    buy_status=1
    # print(buy_status)
print('prev_target=', target_price)
while True:
    try:
        now = datetime.datetime.utcnow()  #한국시간대
        # now = datetime.datetime.now(pytz.timezone('UTC')) # utc 시간대


        if mid - datetime.timedelta(seconds=10) < now < mid:
            # time.sleep(1)
            # target_price = get_target_price(mTicker)
            mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
            ma5 = get_yesterday_ma5(mTicker)
            # print(now, c  urrent_price, target_price, ma5)
            print('next_target=', target_price)
            sell_crypto_currency(mTicker)

        current_price = pyupbit.get_current_price(mTicker)
        # print(now, current_price, target_price)
        # if (current_price > target_price) and (current_price > ma5):
        # if True:
        if current_price > target_price:
            buy_crypto_currency(mTicker, current_price)
        #     print(1)
    except :
        print("err")
    time.sleep(1)