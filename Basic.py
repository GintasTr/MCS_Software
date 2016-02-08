from SimpleCV import *
import cv2



def setup():
    global cam
    cam = Camera()
    time.sleep(2)


def NumpyConversion(imgInput):
    converted = imgInput.getNumpyCv2()
    return converted


def GetImages():
    img = cam.getImage()
    flipped = img.flipHorizontal()
    images = [img, flipped, flipped.binarize()]
    return images  # returns list of 2 - first flipped, 2nd binarized.


def ShowWindow(number, image):
    cv2.imshow("Image number %s" % number, image)
    return


##Software starts here:
setup()

while True:
    Images = GetImages()

    count = 0
    while count < len(Images):
        Images[count] = NumpyConversion(Images[count])
        count += 1

    count = 0
    while count < len(Images):
        ShowWindow(count, Images[count])
        count += 1
    cv2.waitKey(10)
