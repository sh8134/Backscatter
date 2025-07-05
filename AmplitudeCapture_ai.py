# 첫 동작 시 10초간 학습하는 시간이 있습니다. 이 시간 동안 태그가 없는 상태에서의 진폭을 받아 학습하고 이후부터 태그의 존재여부를 감지할 수 있습니다. 1초마다 수신받은 진폭의 평균과 태그 존재여부를 터미널창에 보여줍니다.
import zmq
import numpy as np
import time
from pyod.models.iforest import IForest

DATA_MAX_SIZE = 10
TRAIN_SIZE = 100  # IForest 학습을 위한 초기 샘플 개수

# ZMQ 설정
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"")

print("Receiving amplitude data...")

# 초기 학습 데이터 수집
train_data = []

print("Collecting training data...")
while len(train_data) < TRAIN_SIZE:
    raw = socket.recv()
    data = np.frombuffer(raw, dtype=np.float32)[:DATA_MAX_SIZE] # socket.recv()의 반환값이 여러개의 실수로 나오는 경우가 있습니다. 따라서 최대 10개 까지만 추리고 추린 실수들로만 평균을 내어 IForest에 넣을 데이터로 사용합니다.
    mean_val = np.mean(data)  
    train_data.append([mean_val])  # IForest는 2D 입력 필요
    time.sleep(0.1)

# 모델 학습
clf = IForest()
clf.fit(np.array(train_data))
print("Training complete. Now detecting anomalies...")

# 실시간 예측
while True:
    raw = socket.recv()
    data = np.frombuffer(raw, dtype=np.float32)[:DATA_MAX_SIZE]
    mean_val = np.mean(data)
    prediction = clf.predict([[mean_val]])[0]  # 1: 이상치, 0: 정상
    print("Received mean:", mean_val, "→ Anomaly:" if prediction else "→ Normal:", prediction)
    time.sleep(1)