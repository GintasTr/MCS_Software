import csv
from SimpleCV import *

cam = None
# prepares, selects the camera
def setup():
    global cam
    if cam == None:
        cam = Camera(0, {"width": 640, "height": 480})    # Only for RPI 2592x1944. For calibration - 1024x768
    #cam = Camera                                          # Only for laptop
    time.sleep(1)


# for image acquisition from camera (and flipping)
def GetImage():
    img = cam.getImage()
    #img = cam.getImage()        ##ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    img = img.flipVertical()
    img = img.flipHorizontal()
    return img


# Shows the image until the button is pressed
def show_image_until_pressed(img):
    disp = Display()                                        # Create a display
    while disp.isNotDone():                                 # Loop until display is not needed anymore
        if disp.mouseLeft:                                  # Check if left click was used on display
            disp.done = True                                # Turn off Display
        img.show()                                          # Show the image on Display
    disp.quit()                                        # Exit the display so it does not go to "Not responding"

# Briefly flashes the image
def show_image_briefly(img):
    img.show()                                              # Show the image on Display


setup()
while True:
    img = GetImage()
    barcode = img.findBarcode()
    if barcode: # if we have a barcode
        for i in range(0, len(barcode)):
            barcode[i].draw()
            data = str(barcode[i].data)
            img.dl().text(data, barcode[i].coordinates(), color= Color.RED)
    else:
        img.dl().text("NOT RECOGNISED", (img.width/2, img.height/2), color= Color.RED)

    show_image_briefly(img)