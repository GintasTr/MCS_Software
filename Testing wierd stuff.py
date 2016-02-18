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



coords1 = (141,355)
coords2 = (96,394)
x_dist = abs(coords1[0] - coords2[0])                       # Get maximum X distance
y_dist = abs(coords1[1] - coords2[1])                       # Get maximum Y distance
max_dist = sqrt(x_dist**2 + y_dist**2)                        # Basic calculation of diagonal distance
max_dist = int(round(max_dist))                                                            # Make max dist integer
print x_dist                                                # For debugging
print y_dist
print max_dist
