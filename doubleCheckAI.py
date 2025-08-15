# 최초 실행시 다음의 명령어를 실행해 라이브러리를 설치합니다
# pip3 install pyzmq numpy pyod
# pip3 install scipy scikit-learn
# 실행하려면 터미널 창에 python3 doubleCheckAI.py 명령어를 입력합니다.

# 본 코드를 실행하면 첫 25초 간 세팅시간을 갖습니다.
# 0~10초: 평상시 학습, 10~15초: 태그가 작동하도록 사람이 기기 조작하는것을 기다려줌. 15초~25초: 태그로 인해 증폭된 파장을 학습
# 25초가 지난 후에 실측정 가능합니다.

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
print("🟢 0~10초: 평상시 상태 데이터를 수집합니다.")
normal_data = []
for sec in range(NORMAL_TRAIN_TIME):
    mean_val = get_mean_from_socket()
    normal_data.append([mean_val])
    print(f"[평상시 학습] {sec+1}초 - 평균값: {mean_val:.4f}")
    time.sleep(1)

# ------------------ 10~15초: 센서 교체 안내 ------------------
print("\n🔄 10~15초: 상태 전환을 위해 센서를 교체해주세요.")
for remaining in range(WAIT_TIME, 0, -1):
    print(f"    센서 교체 중... {remaining}초 남음")
    time.sleep(1)

# ------------------ 15~25초: 비정상 학습 ------------------
print("\n🔴 15~25초: 증폭 상태 데이터를 수집합니다.")
abnormal_data = []
for sec in range(ABNORMAL_TRAIN_TIME):
    mean_val = get_mean_from_socket()
    abnormal_data.append([mean_val])
    print(f"[증폭시 학습] {sec+1}초 - 평균값: {mean_val:.4f}")
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
        state = "🟢 평상시 상태로 판단"
    else:
        state = "🔴 증폭된 상태로 판단"

    print(f"[실시간] 평균값: {mean_val:.4f} | 평시점수: {score_normal:.4f}, 증폭점수: {score_abnormal:.4f} → {state}")
    time.sleep(1)
