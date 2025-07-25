import zmq
import numpy as np

# ZMQ 설정
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")  # GNU Radio PUB 주소
socket.setsockopt(zmq.SUBSCRIBE, b"")   # 모든 메시지 구독

print("[INFO] ZMQ 연결 완료. 데이터 수신 중...")

try:
    while True:
        # 바이트 수신 → float32 배열로 변환
        raw = socket.recv()
        data = np.frombuffer(raw, dtype=np.float32)

        # 출력 또는 처리 (이진 결과라고 가정)
        print("수신값:", data.tolist())

        # 사용 예: 1/0에 따라 동작 트리거
        if data[0] == 1.0:
            print("💡 반사 상태 감지 (Tag: ON)")
        elif data[0] == 0.0:
            print("⛔ 흡수 상태 감지 (Tag: OFF)")
        else:
            print("❓ 예상치 못한 값:", data[0])

except KeyboardInterrupt:
    print("\n[종료] 사용자 중단에 의해 종료되었습니다.")
finally:
    socket.close()
    context.term()
