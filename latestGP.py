import zmq
import numpy as np
import time	

DATA_MAX_SIZE = 10000000
DATA = []

    

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"")

print("Receiving amplitude data...")

def collectAllLeftData():
    global DATA
    

    while(len(DATA)<DATA_MAX_SIZE):
        raw = socket.recv()
        DATA.extend(np.frombuffer(raw, dtype=np.float32))     
        


	

        
prev = 0


while True:

    collectAllLeftData()

    if np.mean(DATA) > 0.6:
    	#current = 1
        print(1)
    else:
    	#current = 0
        print(0)

    ###print(DATA[:100])

    #if(prev!=current):
    #    print(current)

    #prev = current


    DATA.clear()
   
    
    	
    
