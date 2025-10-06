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

    global DATA
    global START

    while(time.time() - START < 1):
        
        raw = socket.recv()
        DATA.extend(np.frombuffer(raw, dtype=np.float32))
        
        

    START = time.time()
    
    

def setThreshold():

    THRESHOLD = (np.min(MEAN_VALUES_FOR_SETTING_THRESHOLD) + np.max(MEAN_VALUES_FOR_SETTING_THRESHOLD))/2

    
    MEAN_VALUES_FOR_SETTING_THRESHOLD.clear()

while True:

    INDEX += 1
    currentMean = 0.0
    collectAllLeftData()
    
    currentMean = np.mean(DATA)
    MEAN_VALUES_FOR_SETTING_THRESHOLD.extend(np.frombuffer(currentMean, dtype=np.float32))

    if THRESHOLD == 0.0:
        # I used mean value of sum of np.min(DATA) and np.max(DATA) cause
        # like calculating threshold using my own eye within one second 
        # there always are likely to have previous values.

        THRESHOLD = (np.min(DATA) + np.max(DATA))/2

    if INDEX > 10:

        setThreshold()

        INDEX = 0


    if currentMean > THRESHOLD:
    	
        print(1)
    else:
    	
        print(0)

    #print(DATA[:100])


    DATA.clear()
   
    
    	
    
