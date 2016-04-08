from SimpleCV import *
import numpy as np
import cv2



# prepares, selects the camera
def setup():
    global cam
    cam = Camera()
    time.sleep(1)


# Function to get the image from camera
def GetImage():
    img = cam.getImage()                                            # Get image from camera
    img = cam.getImage()                                            # ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    img = img.flipHorizontal()                                      # Flip image (has to be tested on PI)
    return img

"""
# Main software
setup()
vs = VideoStream("Test.avi", fps = 30)
max_frames = 150

framecount = 0
while(framecount<max_frames):
    framecount = framecount + 1
    cam.getImage().save(vs)
    time.sleep(0.05)
print "Done"
"""



cap = cv2.VideoCapture(0)           # Create a video capture object
cap.set(cv2.cv.CV_CAP_PROP_FPS, 10)
# Define the codec and create VideoWriter object
fourcc = cv2.cv.CV_FOURCC(*'DIVX')
out = cv2.VideoWriter('output.avi',fourcc, 10, (640,480))

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        frame = cv2.flip(frame,1)

        # write the flipped frame
        out.write(frame)

        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()