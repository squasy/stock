import asyncio
import json
import websockets
import ccxt
import pandas as pd
import numpy as np
import time
from time import sleep
from datetime import datetime, timedelta, timezone

# from config import API_KEY, API_SECRET  # API 키 가져오기

with open("binance_api.txt") as f:
    lines = f.readlines()
    API_KEY = lines[0].strip()
    # print(api_key)
    API_SECRET = lines[1].strip()

# 바이낸스 API 설정
binance = ccxt.binance({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "options": {"defaultType": "future"}  # 선물 거래 설정
})

SYMBOL = "BTC/USDT"
K = 0.3  # 변동성 계수 0.3이 최적
USDT_BALANCE = 200  # 투자 금액 ($100)
WEBSOCKET_URL = "wss://fstream.binance.com/ws/btcusdt@trade"


async def get_4hbeforetime_data():
    """전날의 고가, 저가, 시가를 가져옴"""
    ohlcv = binance.fetch_ohlcv(SYMBOL, timeframe="4h", limit=3)
    # print(ohlcv)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

    yesterday = df.iloc[-2]  # 4시간 전 데이터
    # print(ohlcv)
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
                if current_price > 0:
                    # print(f"[{datetime.now()}] 현재 가격: {current_price} / 롱: {target_long} / 숏: {target_short}")

                    if current_price >= target_long:  # 롱 포지션 진입
                        amount = USDT_BALANCE / current_price  # 투자금액 기준 수량 계산
                        await place_order("buy", amount)
                        position = "long"

                    elif current_price <= target_short:  # 숏 포지션 진입
                        amount = USDT_BALANCE / current_price
                        await place_order("sell", amount)
                        position = "short"
                # else:
                #     print(data)


            except Exception as e:
                print(f"웹소켓 오류:{datetime.now()}", e)
                await asyncio.sleep(5)  # 오류 발생 시 재연결
        return position


async def close_position(position):
    """포지션 종료 (4시간마다)"""
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


async def wait_until_4h_after():
    now = datetime.now(timezone.utc)

    daysUp = 0
    if 0 <= now.hour < 4:
        close_time = 4
    elif 4 <= now.hour < 8:
        close_time = 8
    elif 8 <= now.hour < 12:
        close_time = 12
    elif 12 <= now.hour < 16:
        close_time = 16
    elif 16 <= now.hour < 20:
        close_time = 20
    elif 20 <= now.hour:
        daysUp = 1
        close_time = 0
    next_4hour = (now + timedelta(days=daysUp)).replace(hour=close_time, minute=00, second=0, microsecond=0)

    wait_time = (next_4hour - now).total_seconds()

    print(f"⏳ 다음 {close_time}시까지 {wait_time / 3600:.2f}시간 대기 중...")
    await asyncio.sleep(wait_time)  # 9시까지 대기


async def main():
    while True:
        """변동성 돌파 전략 실행"""
        high, low, open_price = await get_4hbeforetime_data()
        target_long = open_price + (high - low) * K  # 롱 목표가
        target_short = open_price - (high - low) * K  # 숏 목표가+
        print(f"📌 오늘 롱 목표가: {target_long} / 숏 목표가: {target_short}")

        print('start')
        position = await listen_websocket(target_long, target_short)  # 롱/숏 포지션 모니터링
        print('start2')
        if position:
            await wait_until_4h_after()  # 이후 4시간까지 대기
            await close_position(position)  # 포지션 청산
            await asyncio.sleep(5)  # 10초후 재시작
            position = None


if __name__ == "__main__":
    asyncio.run(main())
