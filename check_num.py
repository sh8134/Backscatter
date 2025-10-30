# udp_rate_counter.py
import socket, time
HOST = "0.0.0.0"   # 모든 인터페이스
PORT = 5555        # 원하는 포트 번호

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
sock.settimeout(0.1)

count = 0
next_tick = time.monotonic() + 1.0
print(f"[INFO] UDP listen on {HOST}:{PORT}")
while True:
    try:
        sock.recvfrom(65535)  # 내용 무시하고 '1개 수신'으로만 센다
        count += 1
    except socket.timeout:
        pass

    now = time.monotonic()
    if now >= next_tick:
        print(f"msgs/s = {count}")
        count = 0
        next_tick += 1.0
