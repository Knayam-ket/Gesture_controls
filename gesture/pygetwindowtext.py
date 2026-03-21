import pygetwindow as gw
import cv2
while(1):
    activewindow = gw.getActiveWindowTitle()
    print(activewindow)
    if cv2.waitKey(5) & 0xff == 27:
        break
    