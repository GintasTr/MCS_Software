from SimpleCV import *
import cv2
import matplotlib.pyplot as plt
import numpy as np

def calibration():
    while True:
        screen = raw_input("Do you want live feedback? Y/N ")
        screen = screen.lower()
        if screen[0] == "y":
            return True
        elif screen[0] == "n":
            return False
        else:
            print "Incorrect value entered. Please, enter Y or N."


# prepares, selects the camera
def setup():
    global cam
    cam = Camera()
    time.sleep(1)


# for multiple windows OpenCV (includes NumpyConversion)
def ShowWindow(name, image):
    converted = image.getNumpyCv2()
    cv2.imshow("Image: %s" % name, converted)
    return
    ##requires cv2.waitKey(10) !!!

# for image acquisition from camera (and flipping)
def GetImage():
    img = cam.getImage()
    flipped = img.flipHorizontal()
    return flipped

def nothing(x):
    pass

## MAIN SOFTWARE
cv2.namedWindow("Calibration")
cv2.createTrackbar("Test", "Calibration", 0, 255, nothing)
Old_Position = 0
while True:
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break
    Position = cv2.getTrackbarPos("Test", "Calibration")
    if Position == Old_Position:
        pass
    else:
        print Position
        Old_Position = Position

cv2.destroyAllWindows()