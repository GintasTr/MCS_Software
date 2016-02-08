from SimpleCV import *
import cv2

def setup():
    global cam
    cam = Camera()
    time.sleep(2)

def NumpyConversion(imgInput):
    converted = imgInput.getNumpyCv2()
    return converted

def ShowWindow(number, image):
    cv2.imshow("Image number %s" % number, image)
    return

def GetImages():
    img = cam.getImage()
    flipped = img.flipHorizontal()
    return flipped  # returns list of 2 - first flipped, 2nd binarized.

