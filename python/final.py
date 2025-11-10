import zmq
import numpy as np
import time


import serial

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.9)

on_cmd = b'\xA0\x01\x01\xA2'
off_cmd = b'\xA0\x01\x00\xA1'


DATA = []
start = time.time()
index = 0
thr = 0.0
   

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

while True:

    index += 1
    collectAllLeftData()



    if thr == 0.0:
        # I used mean value of sum of np.min(DATA) and np.max(DATA) cause
        # like calculating threshold using my own eye within one second 
        # there always are likely to have previous values.

        thr = (np.min(DATA) + np.max(DATA))/2

    if index > 10:
        if DATA:
            thr = (np.min(DATA) + np.max(DATA))/2

        index = 0



    if np.mean(DATA) > thr:
    	
        print(1)
        ser.write(on_cmd)
        time.sleep(0.01) # turn on for 1 sec
    else:
    	
        print(0)
        ser.write(off_cmd)
        time.sleep(0.01) 

    #print(DATA[:100])


    DATA.clear()
   
    
    	
    
