import zmq
import numpy as np
import time
from pyod.models.iforest import IForest
from collections import deque

DATA_MAX_SIZE = 10
INITIAL_TRAIN_SECONDS = 10
RETRAIN_THRESHOLD_SECONDS = 20

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"")

print("Receiving amplitude data...")

# 1초 간격으로 데이터 수집
train_data = []
print("Collecting initial training data...")

while len(train_data) < INITIAL_TRAIN_SECONDS:
    raw = socket.recv()
    data = np.frombuffer(raw, dtype=np.float32)[:DATA_MAX_SIZE]
    mean_val = np.mean(data)
    train_data.append([mean_val])
    time.sleep(1)

clf = IForest()
clf.fit(np.array(train_data))
print("Initial training complete.")

# 최근 20초간 상태 저장용 (1: 이상, 0: 정상)
recent_predictions = deque(maxlen=RETRAIN_THRESHOLD_SECONDS)
retrain_buffer = deque(maxlen=RETRAIN_THRESHOLD_SECONDS)  # 재학습용 데이터 버퍼

while True:
    raw = socket.recv()
    data = np.frombuffer(raw, dtype=np.float32)[:DATA_MAX_SIZE]
    mean_val = np.mean(data)

    prediction = clf.predict([[mean_val]])[0]  # 1: 이상, 0: 정상
    recent_predictions.append(prediction)
    retrain_buffer.append([mean_val])

    print("Mean:", mean_val, "→ Anomaly:" if prediction else "→ Normal:", prediction)

    # 최근 20초 중 이상이 대부분이면 → 새로운 상태로 재학습
    if len(recent_predictions) == RETRAIN_THRESHOLD_SECONDS:
        abnormal_ratio = sum(recent_predictions) / RETRAIN_THRESHOLD_SECONDS
        if abnormal_ratio >= 0.9:  # 90% 이상이 이상치로 분류됨
            print("🔄 상태 변화 감지됨: 새로운 정상 상태로 적응 중...")
            clf.fit(np.array(retrain_buffer))  # 최근 값을 새로운 기준으로 재학습
            recent_predictions.clear()
            retrain_buffer.clear()
            print("✅ 재학습 완료. 새 기준 적용 중.")

    time.sleep(1)