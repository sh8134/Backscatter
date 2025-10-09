import zmq
import numpy as np
import time	

DATA = []
MEAN_VALUES_FOR_SETTING_THRESHOLD = []
START = time.time()
INDEX = 0
THRESHOLD = 0.0

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"")

print("Receiving amplitude data...")

def collectAllLeftData():
    global DATA, START
    while time.time() - START < 1:
        raw = socket.recv()
        DATA.extend(np.frombuffer(raw, dtype=np.float32))
    START = time.time()

def setThreshold():
    global THRESHOLD

    if len(MEAN_VALUES_FOR_SETTING_THRESHOLD) > 0:
        # 임계값 갱신
        THRESHOLD = (np.min(MEAN_VALUES_FOR_SETTING_THRESHOLD) + np.max(MEAN_VALUES_FOR_SETTING_THRESHOLD)) / 2

        # 가장 오래된 데이터(맨 앞 요소) 제거
        MEAN_VALUES_FOR_SETTING_THRESHOLD.pop(0)

while True:
    INDEX += 1
    collectAllLeftData()

    currentMean = np.mean(DATA)
    MEAN_VALUES_FOR_SETTING_THRESHOLD.append(currentMean)  # frombuffer → append로 수정

    if THRESHOLD == 0.0:
        THRESHOLD = (np.min(DATA) + np.max(DATA)) / 2

    if INDEX > 10:
        setThreshold()
        INDEX = 0

    if currentMean > THRESHOLD:
        print(1)
    else:
        print(0)

    DATA.clear()