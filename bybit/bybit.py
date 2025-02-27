from pybit.unified_trading import WebSocket
from time import sleep



# 메시지 핸들러 함수 정의
def handle_message(message):
    print(2)
    if 'data' in message:
    	data = message['data']
    	for tick_data in data:
    		print("Received Tick Data", tick_data)
    else:
    	print("Recieved Message without 'data' field:", message)
        
def main():
    # WebSocket 객체 생성
    print(1)
    ws = WebSocket(
	    # 실제 거래가 아닌 테스트넷을 사용할 경우 True로 설정
       testnet=False,    
 #       testnet=True,
        channel_type="linear"  # 리니어 채널 설정
    )

    # BTCUSDT 거래 데이터 구독
    ws.trade_stream(
        symbol="BTCUSDT",     # 구독할 심볼 설정
        callback=handle_message  # 데이터 수신 시 호출될 콜백 함수
    ) 

    # 데이터 수신 대기
    try:
        while True:
            sleep(1)  # 1초마다 반복
    except KeyboardInterrupt: # CTRL C 
        print("Interrupted by user")

if __name__ == "__main__":
    main()