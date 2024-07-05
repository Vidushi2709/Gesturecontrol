import cv2
import time
import numpy as np
import handdetectmodule as hdm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam=640, 480
vidz = cv2.VideoCapture(0)
#resize
vidz.set(3,wCam)
vidz.set(4,hCam)  
pTime=0

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()

volrange=volume.GetVolumeRange()
minvol=volrange[0]
maxvol=volrange[1]
vol=0
newvol=400 #initilalize at 400 coz that's our 0 

#changing confidence to get better result
detector=hdm.Handdetect(detectconfi=0.7)

while True:
    success, img = vidz.read()
    img=detector.findhands(img)
    lmlist=detector.findposition(img, False)
    #print(lmlist)
    #4 is the landmark for thumb tip
    #8 is landmark for index finger tip
    if len(lmlist)!=0:
        #print(lmlist[4], lmlist[8])
        x1,y1=lmlist[4][1], lmlist[4][2]
        x2,y2=lmlist[8][1], lmlist[8][2]

        cv2.circle(img, (x1,y1), 15, (255,0,255), cv2.FILLED)
        cv2.circle(img, (x2,y2), 15, (255,0,255), cv2.FILLED)
    #drawing a line between the circles
        cv2.line(img,(x1,y1),(x2,y2),(255,0,255), 2)
        #drawing a circle between the lines
        midX, midY = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.circle(img, (midX, midY), 15, (255, 0, 255), cv2.FILLED)
        
    #now we need to get the length of the line as it's gonna keep changing 
        length=math.hypot(x2-x1, y2-y1)
        #print(length)

        #vol range with hands goes from 50 to 300
        #volume range is= -65 and -0, we need to convert that above into this
        #use numpy ()s

        vol=np.interp(length,[50,300],[minvol,maxvol])
        newvol=np.interp(length, [50,350], [400,150]) #changing the length coz my volume was going out of the screen, LOL
        perecentvol=np.interp(length, [50,300], [0,100])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)


        if(length<=50):
            cv2.circle(img, (midX, midY), 15, (0,255,255), cv2.FILLED)

        cv2.rectangle(img, (50,150), (85,400), (255,255,0),4)
        cv2.rectangle(img, (50,int(newvol)), (85,400), (255,255,0), cv2.FILLED)
        cv2.putText(img, f'{int(perecentvol)}', (40,300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    

    cTime=time.time()
    fps=1/(cTime-pTime)
    pTime=cTime
    cv2.putText(img, str(int(fps)),(10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0), 3)  

    if not success:
        print("Failed to capture image")
        break
   
    img_resized = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    cv2.imshow("hands", img_resized)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
vidz.release()
cv2.destroyAllWindows()
 