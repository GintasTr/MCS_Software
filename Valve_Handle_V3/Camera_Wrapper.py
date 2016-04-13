from SimpleCV import *
import cv2
from Setup import *
from User_Interface_Commands import *
from Calibration import *
from Camera_Wrapper import *
from Image_Processing import *
from Calibration import *


# Function to get the image from the camera
def GetImage():
    img = cam.getImage()                                            # Get image from camera
    img = cam.getImage()                                            # ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    img = img.flipHorizontal()                                      # Flip image (has to be tested on PI)
    return img
