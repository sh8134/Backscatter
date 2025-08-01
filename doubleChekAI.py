import zmq
import numpy as np
import time
from pyod.models.iforest import IForest

# 설정값
DATA_MAX_SIZE = 10
NORMAL_TRAIN_TIME = 10     # 0~10초
WAIT_TIME = 5              # 10~15초 (센서 교체 안내)
ABNORMAL_TRAIN_TIME = 10   # 15~25초

# ZMQ 연결 설정
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"")

# 평균값 추출 함수
def get_mean_from_socket():
    raw = socket.recv()
    data = np.frombuffer(raw, dtype=np.float32)[:DATA_MAX_SIZE]
    return np.mean(data)

# ------------------ 0~10초: 정상 학습 ------------------
print("🟢 0~10초: 정상 상태 데이터를 수집합니다.")
normal_data = []
for sec in range(NORMAL_TRAIN_TIME):
    mean_val = get_mean_from_socket()
    normal_data.append([mean_val])
    print(f"[정상 학습] {sec+1}초 - 평균값: {mean_val:.4f}")
    time.sleep(1)

# ------------------ 10~15초: 센서 교체 안내 ------------------
print("\n🔄 10~15초: 상태 전환을 위해 센서를 교체해주세요.")
for remaining in range(WAIT_TIME, 0, -1):
    print(f"    센서 교체 중... {remaining}초 남음")
    time.sleep(1)

# ------------------ 15~25초: 비정상 학습 ------------------
print("\n🔴 15~25초: 비정상 상태 데이터를 수집합니다.")
abnormal_data = []
for sec in range(ABNORMAL_TRAIN_TIME):
    mean_val = get_mean_from_socket()
    abnormal_data.append([mean_val])
    print(f"[비정상 학습] {sec+1}초 - 평균값: {mean_val:.4f}")
    time.sleep(1)

# ------------------ 모델 학습 ------------------
print("\n📊 모델 학습 중...")
model_normal = IForest()
model_abnormal = IForest()
model_normal.fit(np.array(normal_data))
model_abnormal.fit(np.array(abnormal_data))
print("✅ 모델 학습 완료! 이제 상태를 실시간으로 감지합니다.\n")

# ------------------ 25초 이후: 실시간 감지 ------------------
while True:
    mean_val = get_mean_from_socket()

    # 두 모델에 대한 이상 점수 계산
    score_normal = model_normal.decision_function([[mean_val]])[0]
    score_abnormal = model_abnormal.decision_function([[mean_val]])[0]

    # 점수가 낮을수록 해당 모델과 유사한 상태임
    if score_normal < score_abnormal:
        state = "🟢 정상 상태로 판단"
    else:
        state = "🔴 비정상 상태로 판단"

    print(f"[실시간] 평균값: {mean_val:.4f} | 정상점수: {score_normal:.4f}, 비정상점수: {score_abnormal:.4f} → {state}")
    time.sleep(1)