import zmq
import numpy as np
import time

DATA = []
start = time.time()
index = 0
thr = 0.0

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"")

print("Receiving amplitude data...")

# === 알파벳 매핑 (5비트 → 문자) ===
def bits_to_char(bits):
    """5비트 배열을 문자로 변환"""
    val = int("".join(map(str, bits)), 2)
    if 0 <= val < 26:
        return chr(ord('a') + val)
    return "?"  # 범위 밖이면 ? 처리

def collectAllLeftData():
    global DATA, start
    while(time.time() - start < 1):
        raw = socket.recv()
        DATA.extend(np.frombuffer(raw, dtype=np.float32))
    start = time.time()

# === 디코딩 상태 ===
bitstream = []
decoding = False
ones_count = 0
current_bits = []
decoded_chars = []

while True:
    index += 1
    collectAllLeftData()

    # threshold 초기화
    if thr == 0.0:
        thr = (np.min(DATA) + np.max(DATA)) / 2
    if index > 10:
        thr = (np.min(DATA) + np.max(DATA)) / 2
        index = 0

    # 현재 비트 판별
    bit = 1 if np.mean(DATA) > thr else 0
    print(bit)  # 비트 출력 
    
    # === 디코딩 로직 ===
    if not decoding:
        # 아직 시작 신호 기다리는 중
        if bit == 1:
            ones_count += 1
            if ones_count == 6:
                decoding = True
                bitstream = []
                decoded_chars = []
                print("\n[Start of Frame detected]")
        else:
            ones_count = 0
    else:
        # 프레임 시작 이후 디코딩
        bitstream.append(bit)

        # 문자 단위 디코딩 (6비트씩)
        if len(bitstream) == 6:
            # 첫 비트는 항상 0 (구분자)
            data_bits = bitstream[1:]  # 뒤 5비트
            char = bits_to_char(data_bits)
            decoded_chars.append(char)
            print(f"\n[Decoded char: {char}]")
            bitstream = []

            # 다섯 글자 다 받으면 문자열 출력
            if len(decoded_chars) == 5:
                word = "".join(decoded_chars)
                print(f"[Decoded word: {word}]")
                decoding = False
                ones_count = 0

    DATA.clear()