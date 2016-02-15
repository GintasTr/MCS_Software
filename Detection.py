from SimpleCV import *
import cv2

# to turn on/off video feedback for calibration
def calibration():
    #question for user
    while True:
        screen = raw_input("Do you want video feedback? Y/N ")
        screen = screen.lower()
        if screen[0] == "y":
            return True
        elif screen[0] == "n":
            return False
        else:
            print "Incorrect value entered. Please, enter Y or N."

# to create trackbar
def createTrackbar(name):

    # required for Trackbar
    def nothing(x):
        pass

    cv2.namedWindow("Trackbars")
    cv2.createTrackbar("%s" %name, "Trackbars", 0, 255, nothing)


# to get specific trackbar position
def bar_position(name):
    Position = cv2.getTrackbarPos("%s" %name, "Trackbars")

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


## MAIN SOFTWARE

screen = calibration()
setup()

## Main loop:
while True:
    Img = GetImage()

    Img = Img.toHSV()

    ##MAIN FILTERING STAGE - saturation, value and color have to be calibrated.
    Filtered = Img.hueDistance(Color.GREEN, minsaturation=80, minvalue=10)
    Filtered = Filtered.invert()
    Filtered = Filtered.dilate(1)
    Filtered = Filtered.erode(1)

    ##SECOND FILTERING STAGE - threshold value and minimum/maximum size have to be calibrated.
    blobs_all = Filtered.findBlobs(threshval=200, minsize=7000)
    if blobs_all is None:
        if screen == True:
            Img.dl().setFontSize(40)
            Img.dl().text(text= "No Green Things found", color = Color.RED, location = (Img.width/15, Img.height/15))
        else:
            print "No Green Things found."
    else:
        x=0
        while x < len(blobs_all):
            if screen == True:
                Img.dl().rectangle2pts(blobs_all[x].topLeftCorner(), blobs_all[x].bottomRightCorner(),Color.GREEN, width = 5)
                Img.dl().circle(blobs_all[x].coordinates(), radius = 2, width = 5, filled = True, color = Color.RED, )
            else:
                print "Object found at:", blobs_all[x].coordinates(), "and its area is:", blobs_all[x].area()
            x += 1

    if screen == True:
        ShowWindow("Hue", Filtered)
        Img.show()