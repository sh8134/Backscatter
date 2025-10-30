# rx_phase_fixed_250_minimal.py
# pip install pyzmq numpy
import zmq
import numpy as np
from datetime import datetime

HOST, PORT = "127.0.0.1", 5555

FS       = 200.0     # 샘플레이트(참고용)
N_TRUE   = 250.0     # ★ 확인된 심볼 길이(샘플) -> 고정 시계로 사용
GAMMA    = 0.15      # 슈미트 히스테리시스 비율(레벨 차의 15%)
ETA0     = 0.01      # 레벨0 평균 업데이트율(천천히 추적)
ETA1     = 0.01      # 레벨1 평균 업데이트율
HOLD     = 3         # 에지 바운싱 방지(샘플)
MIN_EDGE = int(0.25 * N_TRUE)  # 너무 가까운 에지(글리치) 무시

def bootstrap_levels(x: np.ndarray):
    """초기 임계: median±2*MAD (치우침/스파이크에 강함)"""
    x = np.asarray(x, np.float32)
    if x.size == 0:
        return 0.25, 0.75
    m   = np.median(x)
    mad = np.median(np.abs(x - m)) + 1e-6
    dev = 1.4826 * mad
    mu0 = m - 2*dev
    mu1 = m + 2*dev
    if mu1 < mu0:
        mu0, mu1 = mu1, mu0
    return float(mu0), float(mu1)

def emit(bit):
    # 시간과 비트만 출력
    print(f"{datetime.now().strftime('%H:%M:%S')} {bit}")

def main():
    # ---- ZMQ 구독 준비 ----
    ctx = zmq.Context.instance()
    sub = ctx.socket(zmq.SUB)
    sub.setsockopt(zmq.SUBSCRIBE, b"")
    sub.setsockopt(zmq.RCVHWM, 100000)
    sub.connect(f"tcp://{HOST}:{PORT}")

    # ---- 1) 초기 1초 정도 모아서 임계/레벨 추정 ----
    acc = np.empty(0, np.float32)
    need = int(FS * 1.0)
    while acc.size < need:
        arr = np.frombuffer(sub.recv(), dtype=np.float32)
        if arr.size:
            acc = arr.copy() if acc.size == 0 else np.concatenate([acc, arr])

    mu0, mu1 = bootstrap_levels(acc)
    theta = 0.5*(mu0 + mu1)
    span  = max(mu1 - mu0, 1e-6)
    hi, lo = theta + GAMMA*span, theta - GAMMA*span
    state = 1 if acc[-1] >= theta else 0
    hold  = 0

    # ---- 2) 운용: 페이즈 누적 출력 + 에지로 페이즈 보정 ----
    phase = 0.0
    sample_count  = 0
    last_edge_idx = None

    try:
        while True:
            arr = np.frombuffer(sub.recv(), dtype=np.float32)
            if arr.size == 0:
                continue

            for v in arr:
                # 문턱 갱신(레벨 추적은 천천히)
                theta = 0.5*(mu0 + mu1)
                span  = max(mu1 - mu0, 1e-6)
                hi, lo = theta + GAMMA*span, theta - GAMMA*span

                # 슈미트 전이 감지(히스테리시스 + 홀드오프 + 최소 간격)
                edge = False
                s = state
                if hold > 0:
                    hold -= 1
                else:
                    ok_gap = (last_edge_idx is None) or ((sample_count - last_edge_idx) >= MIN_EDGE)
                    if s == 0 and v >= hi and ok_gap:
                        s, edge = 1, True
                    elif s == 1 and v <= lo and ok_gap:
                        s, edge = 0, True

                # 방문 상태 레벨만 업데이트
                if s == 1:
                    mu1 = (1-ETA1)*mu1 + ETA1*float(v)
                else:
                    mu0 = (1-ETA0)*mu0 + ETA0*float(v)
                if mu1 < mu0:
                    mu0, mu1 = mu1, mu0

                # ---- 페이즈 기반 심볼 출력(매 N_TRUE샘플마다 현재 상태로 1비트) ----
                phase += 1.0 / N_TRUE
                while phase >= 1.0:
                    emit(s)   # 긴 1-run/0-run 동안에도 지속 출력
                    phase -= 1.0

                # ---- 에지에서 시계 보정: 페이즈 리셋(경계 정렬) ----
                if edge:
                    hold = HOLD
                    last_edge_idx = sample_count
                    phase = 0.0  # 경계를 '지금'으로 동기화

                state = s
                sample_count += 1

    except KeyboardInterrupt:
        pass
    finally:
        sub.close(0)
        ctx.term()

if __name__ == "__main__":
    main()
