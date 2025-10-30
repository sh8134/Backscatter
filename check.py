# pip install pyzmq numpy
import zmq, numpy as np, time, datetime
from collections import deque

HOST = "127.0.0.1"   # GRC ZMQ PUB Sink가 바인드한 호스트
PORT = 5555          # GRC ZMQ PUB Sink의 포트
TARGET_RATE = 200    # 기대 샘플 레이트(참고용 출력)
WINDOW_SEC = 1.0     # 집계 윈도우(초)
KEEP_SECONDS = 60    # 최근 N초 분량만 메모리에 보관 (원하면 크게/작게 조절)

def main():
    ctx = zmq.Context.instance()
    sock = ctx.socket(zmq.SUB)
    sock.setsockopt(zmq.SUBSCRIBE, b"")     # 모든 토픽 구독
    sock.setsockopt(zmq.RCVHWM, 100000)     # 수신 대기열 크게
    sock.connect(f"tcp://{HOST}:{PORT}")

    poller = zmq.Poller()
    poller.register(sock, zmq.POLLIN)

    # 최근 초별 데이터를 보관하는 버퍼 (원한다면 파일 저장 로직으로 교체 가능)
    per_sec_buffers = deque(maxlen=KEEP_SECONDS)

    # 현재 윈도우 누적용
    bucket = []  # numpy 배열 조각들을 담아두었다가 1초마다 concatenate
    window_start = time.monotonic()
    next_tick = window_start + WINDOW_SEC

    print(f"[INFO] Subscribed to tcp://{HOST}:{PORT}. Counting samples per {WINDOW_SEC:.0f}s…")
    try:
        while True:
            # 남은 시간 동안만 poll하여 윈도우 경계에서 빠르게 끊어 집계
            now = time.monotonic()
            timeout_ms = max(0, int((next_tick - now) * 1000))
            socks = dict(poller.poll(timeout_ms))

            if sock in socks and socks[sock] == zmq.POLLIN:
                msg = sock.recv()  # 한 프레임(메시지)
                # GNU Radio ZMQ PUB Sink는 원시 float32 스트림을 보냄(여러 개가 한꺼번에 담길 수 있음)
                arr = np.frombuffer(msg, dtype=np.float32)
                # frombuffer는 메시지 버퍼를 참조하므로 복사해서 보관(다음 recv 전에 안전)
                if arr.size:
                    bucket.append(arr.copy())

            # 윈도우 종료 시점이면 집계/출력
            now = time.monotonic()
            if now >= next_tick:
                if bucket:
                    samples = np.concatenate(bucket)
                else:
                    samples = np.empty(0, dtype=np.float32)

                per_sec_buffers.append(samples)

                ts = datetime.datetime.now().strftime("%H:%M:%S")
                n = samples.size
                if n > 0:
                    print(f"[{ts}] {n:4d} samples/s  "
                          f"(target≈{TARGET_RATE}, Δ={n - TARGET_RATE:+d})  "
                          f"mean={samples.mean():.6f}  min={samples.min():.6f}  max={samples.max():.6f}")
                else:
                    print(f"[{ts}]    0 samples/s  (target≈{TARGET_RATE}, Δ={-TARGET_RATE:+d})")

                # 다음 윈도우로 넘어가기 (드리프트 누적 방지: 고정 간격 스텝)
                bucket.clear()
                # 지연이 있었다면 여러 초를 한 번에 건너뛸 수 있도록 반복 증가
                while now >= next_tick:
                    next_tick += WINDOW_SEC

    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user.")
    finally:
        sock.close(0)
        ctx.term()

if __name__ == "__main__":
    main()
