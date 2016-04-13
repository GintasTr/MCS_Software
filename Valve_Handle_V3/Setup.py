from SimpleCV import *
import cv2
from User_Interface_Commands import *
from Calibration import *
from Camera_Wrapper import *
from Image_Processing import *
from Calibration import *

# prepares, selects the camera
def setup():
    global cam
    cam = Camera()
    time.sleep(1)
