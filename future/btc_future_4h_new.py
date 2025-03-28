import ccxt
import time
from datetime import datetime
import pandas as pd

# 바이낸스 API 키 설정 (실제 키로 교체 필요)
with open("binance_api.txt") as f:
    lines = f.readlines()
    API_KEY = lines[0].strip()
    # print(api_key)
    API_SECRET = lines[1].strip()

# 바이낸스 선물 연결
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

# 거래 설정
symbol = 'BTC/USDT'
timeframe = '4h'  # 4시간봉
k_value = 0.3  # 변동성 돌파 k 값
trade_amount = 200  # 기본 거래액 (USDT)
leverage = 1  # 레버리지 (필요 시 조정)

# 레버리지 설정
exchange.fapiprivate_post_leverage({
    'symbol': symbol.replace('/', ''),
    'leverage': leverage
})


def fetch_ohlcv():
    """4시간봉 데이터 가져오기"""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=2)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


def calculate_vbs(df, k):
    """변동성 돌파 가격 계산"""
    last_candle = df.iloc[-2]  # 이전 4시간봉
    range_size = last_candle['high'] - last_candle['low']
    breakout_price = last_candle['close'] + (range_size * k)
    return breakout_price


def get_balance():
    """USDT 잔액 확인"""
    balance = exchange.fetch_balance()
    return balance['total']['USDT']


def place_limit_order(side, price, amount):
    """지정가 주문"""
    try:
        order = 1
        # order = exchange.create_order(
        #     symbol=symbol,
        #     type='limit',
        #     side=side,
        #     amount=amount,
        #     price=price
        # )
        print(f"{side.upper()} 주문 성공: {order['id']}")
        return order
    except Exception as e:
        print(f"주문 실패: {e}")
        return None


def check_position():
    """현재 포지션 확인"""
    positions = exchange.fetch_positions([symbol])
    for pos in positions:
        if pos['symbol'] == symbol and float(pos['contracts']) > 0:
            return pos
    return None


def close_position():
    """포지션 청산"""
    position = check_position()
    if position:
        side = 'sell' if position['side'] == 'long' else 'buy'
        amount = float(position['contracts'])
        exchange.create_market_order(symbol, side, amount)
        print("포지션 청산 완료")


def main(trade_amount=200):
    print("변동성 돌파 봇 시작")
    last_candle_time = None

    while True:
        try:
            # 현재 시간 확인
            current_time = datetime.utcnow()

            # 4시간봉 데이터 가져오기
            df = fetch_ohlcv()
            current_candle_time = df.iloc[-1]['timestamp']

            # 새로운 4시간봉 시작 시
            if last_candle_time != current_candle_time:
                close_position()  # 이전 포지션 청산
                breakout_price = calculate_vbs(df, k_value)
                print(f"새로운 4시간봉 시작 - 돌파 가격: {breakout_price}")

                # 거래 수량 계산 (USDT 기준)
                current_price = df.iloc[-1]['close']
                amount = (trade_amount * leverage) / current_price

                # 지정가 롱 포지션 주문
                order = place_limit_order('buy', breakout_price, amount)
                last_candle_time = current_candle_time

                # 4시간 동안 주문 체크
                start_time = time.time()
                while time.time() - start_time < 4 * 3600:  # 4시간
                    if check_position():  # 포지션 진입 확인
                        print("포지션 진입 성공")
                        break
                    time.sleep(60)  # 1분 대기

                # 4시간 내 포지션 진입 실패 시
                if not check_position():
                    close_position()
                    print("4시간 내 진입 실패, 다음 캔들 대기")

            # 24시간 루프 유지
            time.sleep(60)  # 1분마다 체크

        except Exception as e:
            print(f"에러 발생: {e}")
            time.sleep(60)


if __name__ == "__main__":
    # 거래액 수정 가능 (예: 300 USDT로 실행)
    main(trade_amount=300)  # 기본값 200 대신 300으로 실행 예시