import zmq
import numpy as np
import time	

DATA_MAX_SIZE = 10

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"")

print("Receiving amplitude data...")

while True:
    raw = socket.recv()
    data = np.frombuffer(raw, dtype=np.float32)
    print("Received amplitude:", data[:DATA_MAX_SIZE], "...")
    
    
    if np.mean(data[:DATA_MAX_SIZE]) > 0.05:
    	print(1)
    else:
    	print(0)
    	
    time.sleep(1) 
