from SimpleCV import *
import cv2

"""
cam = Camera()
time.sleep(1)
img = cam.getImage()
img = cam.getImage()
display = Display()
#pressed = pg.key.get_pressed()
print "I launched a window"
while display.isNotDone():
    #if(pressed[13] == True): #CODE FOR ESC. CAN BE USED FOR OTHER??
    #    display.done = True

    if display.mouseRight:
        display.done = True
    img.show()
Display().quit()
while True:
    None
"""

""" CODE TO FIND THE PRESSED KEY CODE
import cv2
img = cv2.imread('Lenna.png') # load a dummy image
while(1):
    cv2.imshow('img',img)
    k = cv2.waitKey(33)
    if k==27:    # Esc key to stop
        break
    elif k==-1:  # normally -1 returned,so don't print it
        continue
    else:
        print k # else print its value
"""

img = Image("Cropped2.jpg")
img = img.toGray()
img_gray = img.getGrayNumpy()
average_gray = np.mean(img_gray)


print img_gray.shape
print img_gray
print average_gray

    # print hsv[:,:,0], "HUE"
    # print hsv[:,:,1], "SAT"
    # print hsv[:,:,2], "VAL"

    # avgHue = np.mean(hsv[:,:,0])
    # print avgHue, "AVG Hue"
    #
    # avgSat = np.mean(hsv[:,:,1])
    # stdSat = np.std(hsv[:,:,1])
    # minSat = np.min(hsv[:,:,1])
    # avgVal = np.mean(hsv[:,:,2])
    # print avgSat, "avgSat"
    # # print stdSat, "stdSat"
    # # print minSat, "minSat"
    # print avgVal, "avgVal"

