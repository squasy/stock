import asyncio
import json
import websockets
import ccxt
import pandas as pd
import numpy as np
import time
from time import sleep
from datetime import datetime, timedelta
#from config import API_KEY, API_SECRET  # API 키 가져오기

with open("binance_api.txt") as f:
    lines = f.readlines()
    API_KEY = lines[0].strip()
    # print(api_key)
    API_SECRET  = lines[1].strip()

# 바이낸스 API 설정
binance = ccxt.binance({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "options": {"defaultType": "future"}  # 선물 거래 설정
})

SYMBOL = "BTC/USDT"
K = 0.5  # 변동성 계수
USDT_BALANCE = 200  # 투자 금액 ($100)
WEBSOCKET_URL = "wss://fstream.binance.com/ws/btcusdt@trade"


async def get_yesterday_data():
    """전날의 고가, 저가, 시가를 가져옴"""
    ohlcv = binance.fetch_ohlcv(SYMBOL, timeframe="1d", limit=3)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

    yesterday = df.iloc[-2]  # 어제 데이터
    return yesterday["high"], yesterday["low"], df.iloc[-1]["open"]
async def place_order(order_type, amount):
    """시장가 주문 실행 (롱 또는 숏)"""
    try:
        order = binance.create_order(SYMBOL, "market", order_type, amount)
        print(f"{order_type.upper()} 주문 완료! 수량: {amount}")
    except Exception as e:
        print("주문 실패:", e)

async def listen_websocket(target_long, target_short):
    """웹소켓을 통해 실시간 가격을 모니터링하고 목표가 도달 시 롱 또는 숏 포지션 진입"""
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print(f"✅ 웹소켓 연결됨. 롱 목표: {target_long} / 숏 목표: {target_short}")
        position = None
        while position is None:
            try:
                response = await ws.recv()
                data = json.loads(response)
                current_price = float(data["p"])  # 현재 체결 가격

                # print(f"[{datetime.now()}] 현재 가격: {current_price} / 롱: {target_long} / 숏: {target_short}")

                if current_price >= target_long:  # 롱 포지션 진입
                    amount = USDT_BALANCE / current_price  # 투자금액 기준 수량 계산
                    await place_order("buy", amount)
                    position = "long"

                elif current_price <= target_short:  # 숏 포지션 진입
                    amount = USDT_BALANCE / current_price
                    await place_order("sell", amount)
                    position = "short"

            except Exception as e:
                print("웹소켓 오류:", e)
                await asyncio.sleep(5)  # 오류 발생 시 재연결
        return position

async def close_position(position):
    """포지션 종료 (다음날 9시)"""
    try:
        balance = binance.fetch_balance(params={"type": "future"})
        positions = balance["info"]["positions"]
        for pos in positions:
            if pos["symbol"] == "BTCUSDT" and float(pos["positionAmt"]) != 0:
                amount = abs(float(pos["positionAmt"]))  # 보유 수량 가져오기
                order_type = "sell" if position == "long" else "buy"  # 롱이면 매도, 숏이면 매수
                await place_order(order_type, amount)
                print(f"🔴 {datetime.now()} 포지션 청산 완료 ({position.upper()})")
    except Exception as e:
        print("포지션 청산 오류:", e)

async def wait_until_9am():
    """다음날 9시까지 대기"""
    now = datetime.now()
    next_9am = (now + timedelta(days=1)).replace(hour=8, minute=55, second=0, microsecond=0)
    wait_time = (next_9am - now).total_seconds()
    print(f"⏳ 다음 9시까지 {wait_time / 3600:.2f}시간 대기 중...")
    await asyncio.sleep(wait_time)  # 9시까지 대기

async def main():
    """변동성 돌파 전략 실행"""
    high, low, open_price = await get_yesterday_data()
    # print(open_price)
    # print(high)
    # print(low)
    target_long = open_price + (high - low) * K  # 롱 목표가
    target_short = open_price - (high - low) * K  # 숏 목표가
    print(f"📌 오늘 롱 목표가: {target_long} / 숏 목표가: {target_short}")

    # while True:
    position = await listen_websocket(target_long, target_short)  # 롱/숏 포지션 모니터링
    if position:
        await wait_until_9am()  # 다음날 9시까지 대기
        await close_position(position)  # 포지션 청산

if __name__ == "__main__":
    asyncio.run(main())
