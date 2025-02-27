import asyncio
import json
import websockets
import ccxt
import pandas as pd
import numpy as np
import time
from datetime import datetime
from config import API_KEY, API_SECRET  # API 키 가져오기

# 바이낸스 API 설정
binance = ccxt.binance({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "options": {"defaultType": "future"}  # 선물 거래 설정
})

SYMBOL = "BTCUSDT"
K = 0.5  # 변동성 계수
USDT_BALANCE = 100  # 투자 금액 ($100)
WEBSOCKET_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"

async def get_yesterday_data():
    """전날의 고가, 저가, 시가를 가져옴"""
    ohlcv = binance.fetch_ohlcv(SYMBOL, timeframe="1d", limit=3)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    
    yesterday = df.iloc[-2]  # 어제 데이터
    return yesterday["high"], yesterday["low"], df.iloc[-1]["open"]

async def place_order(price, amount):
    """시장가 주문 실행"""
    try:
        order = binance.create_market_buy_order(SYMBOL, amount)
        print(f"매수 주문 완료! 가격: {price}, 수량: {amount}")
    except Exception as e:
        print("주문 실패:", e)

async def listen_websocket(target_price):
    """웹소켓을 통해 실시간 가격을 모니터링하고 목표가 도달 시 매수"""
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print(f"웹소켓 연결됨. 목표 가격: {target_price}")
        while True:
            try:
                response = await ws.recv()
                data = json.loads(response)
                current_price = float(data["p"])  # 체결 가격

                print(f"[{datetime.now()}] 현재 가격: {current_price} / 목표가: {target_price}")

                if current_price >= target_price:
                    amount = USDT_BALANCE / current_price  # 투자금액 기준 수량 계산
                    await place_order(current_price, amount)
                    break  # 주문 후 루프 종료

            except Exception as e:
                print("웹소켓 오류:", e)
                await asyncio.sleep(5)  # 오류 발생 시 재연결

async def main():
    """변동성 돌파 전략 실행"""
    high, low, open_price = await get_yesterday_data()
    target_price = open_price + (high - low) * K
    print(f"오늘 매수 목표가: {target_price}")

    await listen_websocket(target_price)  # 웹소켓으로 가격 모니터링

if __name__ == "__main__":
    asyncio.run(main())