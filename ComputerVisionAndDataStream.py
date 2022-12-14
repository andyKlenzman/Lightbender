#FEATURES:
# -syncronous file playback
# -smoothing
# -hand type data
# -Arduino Compatabiltiy: ButtonHandControl1.1


from array import array
import numpy as np
import pandas as pd
import serial
import time
import sys
import cv2
import matplotlib.pyplot as plt

# arrays for smoothing out hands location and type data
lsmoothFactor = 9
lxhistory= np.zeros((6,lsmoothFactor))
lyhistory= np.zeros((6,lsmoothFactor))
lhhistory= np.zeros((1,lsmoothFactor))

rsmoothFactor = 9
rxhistory= np.zeros((6,rsmoothFactor))
ryhistory= np.zeros((6,rsmoothFactor))
rhhistory= np.zeros((1,rsmoothFactor))


width=640
height=360 

class mpHands:
    import mediapipe as mp
    def __init__(self,maxHands=2,tol1=.5,tol2=.5):
        self.hands=self.mp.solutions.hands.Hands(False,maxHands,tol1,tol2)
    def Marks(self,frame):
        myHands=[]
        handsType=[]
        frameRGB=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        results=self.hands.process(frameRGB)
        
        if results.multi_hand_landmarks != None:
            
            for hand in results.multi_handedness:
                handType=hand.classification[0].label

                print(handType)
                handsType.append(handType)
            
            for handLandMarks in results.multi_hand_landmarks:
                myHand=[]
                for landMark in handLandMarks.landmark:
                    myHand.append((int(landMark.x*width),int(landMark.y*height)))
                myHands.append(myHand)
        
        return(myHands,handsType)


print("Connected to Arduino...")
arduino = serial.Serial(port='/dev/cu.usbserial-0001', baudrate=500000)
#ask for input
userinput = input("--((Write file))--((Read file))--((Freestyle))--")


if (userinput=='r'):
    # variable for storing timestamps to calculate sleep
    testTimeStart=time.time()

    tOld=0
    header_list = ["t", "g", "z", "x", "y"]
    df=pd.read_csv("demofile1", names=header_list)
    df.reset_index()
    print(len(df))
    framecounter=0
    while 1:
        for row in df.itertuples():
            tNew=row[1]
            h=row[2]
            z=row[3]
            x=row[4]
            y=row[5]
            data = "<{0:d},{1:d},{2:d},{3:d}>".format(h,z,x,y)
            arduino.write(data.encode())
            
            time.sleep((abs(tNew-tOld)*.909))
            tOld=tNew
        

    testTimeEnd=time.time()
    timeTotal=testTimeEnd-testTimeStart
    print(timeTotal)
    print(len(df))



if ((userinput=='w') or (userinput=='f')):
    #create file and enable framecounter only if the user says they'd like to write a file
    if(userinput=='w'):
        # open replay file for writing and prep timer to create timestamp
        f=open("demofile1", "w")
        TimerStarted=0
        timestamp=0
        

    
    findHands=mpHands()
    time.sleep(2)
   

    #importing the Haarcascade for face detection
    cam=cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    print("Getting camera image...")

    #Read the captured image, convert it to Gray image and find faces
    while 1:
        ignore, frame = cam.read()
        frame=cv2.resize(frame,(width,height))
        frame = cv2.flip(frame, 1)

        # start timestamp
        if(TimerStarted==0):
            StartTime = time.time()
            TimerStarted=1
        
        handData, handsType=findHands.Marks(frame)
        for hand,handType in zip(handData,handsType):
            arr=[]
            if handType=='Right':
                handColor=(255,255,255)
                h=1

            if handType=='Left':
                handColor=(255,255,255)
                h=0
            
            for ind in [0,4,8,12,16,20]:
                cv2.circle(frame,hand[ind],8, handColor ,5)
                print(ind)
                if(ind==0):
                    z=0
                if(ind==4):
                    z=1
                if(ind==8):
                    z=2
                if(ind==12):
                    z=3
                if(ind==16):
                    z=4
                if(ind==20):
                    z=5
                x=hand[ind][0]
                y=hand[ind][1]

                
                # what about h smoothing? Will that be used to determine where the data goes? Lets do some runs and see what happens
                if(h==0):
                    lxhistory[z] = np.roll(lxhistory[z],-1)
                    lxhistory[z][-1] = x
                    xsmooth = int(np.average(lxhistory[z])) #leaving x smooth without hand type distinct. Shouldn't need it.

                    lyhistory[z] = np.roll(lyhistory[z],-1)
                    lyhistory[z][-1] = y
                    ysmooth = int(np.average(lyhistory[z]))
                if(h==1):
                    rxhistory[z] = np.roll(rxhistory[z],-1)
                    rxhistory[z][-1] = x
                    xsmooth = int(np.average(rxhistory[z])) #leaving x smooth without hand type distinct. Shouldn't need it.

                    ryhistory[z] = np.roll(ryhistory[z],-1)
                    ryhistory[z][-1] = y
                    ysmooth = int(np.average(ryhistory[z]))


                # send data to arduino
                data = "<{0:d},{1:d},{2:d},{3:d}>".format(h,z,xsmooth,ysmooth)
                arduino.write(data.encode())

                # Write data to replay file and count DPS
                if(userinput=='w'):
                    EndTime=time.time()
                    timestamp=EndTime-StartTime
                    data ="{0:f},{1:d},{2:d},{3:d},{4:d}\n".format(timestamp,h,z,xsmooth,ysmooth)
                    f.write(data)
        print(timestamp)
           

    #Display the stream.
        cv2.imshow('BEAUTIFUL',frame)
    #Hit 'Esc' to terminate execution
        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    cam.release()

