import zmq
import numpy as np
import time	

DATA_MAX_SIZE = 4000000
DATA = []
start = time.time()
   

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"")

print("Receiving amplitude data...")

def collectAllLeftData():
    global DATA
    global start

    while(time.time() - start < 1):
        raw = socket.recv()
        DATA.extend(np.frombuffer(raw, dtype=np.float32))     
        

    start = time.time()


	

        
prev = 0


while True:

    collectAllLeftData()

    if np.mean(DATA) > 0.75:
    	#current = 1
        print(1)
    else:
    	#current = 0
        print(0)

    #print(DATA[:100])
    #print(len(DATA))

    #if(prev!=current):
    #    print(current)

    #prev = current


    DATA.clear()
   
    
    	
    
