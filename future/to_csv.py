import ccxt
import pandas as pd
import time

# 바이낸스 객체 생성
exchange = ccxt.binance({
    "rateLimit": 1200,
    "options": {"defaultType": "future"}  # 선물 데이터 가져오기
})
#
symbol = "BTC/USDT"  # 비트코인 선물 심볼
timeframe = "4h"  # 일봉
start_time = exchange.parse8601("2021-11-01T00:00:00Z")  # 시작 날짜
end_time = exchange.parse8601("2022-11-02T00:00:00Z")  # 종료 날짜
limit = 1100  # 한 번에 가져올 최대 데이터 수
all_ohlcv = []

#while start_time < end_time:
ohlcv = exchange.fetch_ohlcv(symbol, timeframe, start_time, limit)
#    print(ohlcv)
#   if not ohlcv:
#      print('no data')
 #     break  # 더 이상 데이터가 없으면 종료
all_ohlcv.extend(ohlcv)
    
#   last_timestamp = ohlcv[-1][0]  # 마지막 데이터의 타임스탬프
#    if last_timestamp >= end_time:
#        print(last_timestamp)
#        print(end_time)
#        break  # end_time을 초과하면 종료
print(1)
time.sleep(10)
print(2)
start_time = exchange.parse8601("2022-05-01T00:00:00Z")  # 시작 날짜
ohlcv = exchange.fetch_ohlcv(symbol, timeframe, start_time, limit)
all_ohlcv.extend(ohlcv)
print(3)
#    start_time = last_timestamp + 10  # 마지막 데이터 이후부터 다시 가져오기
# 데이터프레임 변환
df = pd.DataFrame(all_ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

# CSV 저장
df.to_csv("btc_futures_"+timeframe+".csv", index=False)

print(df.head())  # 데이터 확인