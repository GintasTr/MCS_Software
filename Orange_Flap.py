from SimpleCV import *
import cv2


# to turn on/off video feedback for calibration
def debug():
    # question for user
    while True:
        screen = raw_input("Do you want video feedback? Y/N ")
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
    print "Taking image NOW"
    img = cam.getImage()
    img = cam.getImage()        ##ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    img = img.flipHorizontal()
    return img


def IsFlapClear(flapImg):
    print "Look at the image and inspect whether the flap is clearly visible in the image." \
          " Then left click ANYWHERE ON THE PICTURE to close it and answer the question."
    disp = Display()  # Create a display
    while disp.isNotDone(): # Loop until display is not needed anymore
        if disp.mouseLeft:  #   Check if left click was used on display
            disp.done = True    # Turn off Display
        flapImg.show()  # Show the image on Display
    Display().quit()    # Exit the display so it does not go to "Not responding"

    while True: # Loop until valid response
        userInput = raw_input("Was the flap clearly visible in the image? Please, enter Y or N.\n")
        userInput = userInput.lower()
        if userInput[0] == "y":
            return True
        elif userInput[0] == "n":
            return False
        else:
            print "Incorrect value entered."

## CAN ADD ESC OR ENTER KEYBOARD TO EXIT.

def AcquireFlatImage():  # Acquire flat flap image for calibration
    flat_image_done = False
    while (not flat_image_done):  # Repeat until flat flap image is acquired correctly
        raw_input(
            "Point camera the way it is going to be during the orange flap examination, "
            "put the flap flat on the sub module and press Enter to take the image")
        flat_image = GetImage()  # Get image of the flat flap
        if IsFlapClear(flat_image): # Check if flat image is correct
            flat_image_done = True
        else:
            None
    return flat_image

def get_calibration_coordinates(flatImg):
    print "In the shown image, left click on the orange flap in the image to calibrate" \
      " its colour and then Escape or Right click to turn off the image"
    disp = Display()  # Create a display
    while disp.isNotDone(): # Loop until display is not needed anymore
        flatImg.clearLayers()
        if disp.mouseLeft:  #   Show coords on screen
            mouse_coords = [disp.mouseX, disp.mouseY]
            text = "X:" + str(mouse_coords[0]) + " Y:" + str (mouse_coords[1])
            flatImg.dl().text(text, (mouse_coords[0] + 10, mouse_coords[1] + 10), color=Color.RED)
            flatImg.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]], color = Color.RED, dimensions = [20,20])
        if disp.mouseRight: # Turn off the screen
            disp.done = True    # Turn off Display
        flatImg.save(disp)  # Show the image on Display
    Display().quit()    # Exit the display so it does not go to "Not responding"
    return mouse_coords

def ColorAveraging(flat_image, Calibration_coords):
    crop_length = 20 #Adjust cropping area (x,y,w,h)
    cropped = flat_image.crop(Calibration_coords[0],
                              Calibration_coords[1], crop_length,
                              crop_length, centered= True)
    cropped = cropped.getNumpyCv2()
    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)

    hsvmean = np.mean(cropped, axis = 0)
    hsvStd = np.std(cropped, axis = 0)

    hsvStd = np.std(hsvStd, axis = 0)
    hsvmean = np.mean(hsvmean, axis = 0)

    print hsvStd
    print hsvmean

    meanHue = hsvmean[0]
    meanSat = hsvmean[1]
    stdSat = hsvStd[1]

    print meanHue, "- mean Hue"
    print meanSat, "- mean Sat"
    print stdSat, "- std Sat"
    #raw_input("check results")   --FOR DEBUGGING

    values = {"AvHue": meanHue, "AvSat": meanSat, "StdSat": stdSat}
    return values

def apply_filter(Calibration_values, img):
    Std_constant = 2 #how many STD of values we allow
    min_value = 30 #minimal illumination of the object
    img = img.toHSV()
    Filtered = img.hueDistance(color = Calibration_values["AvHue"],
                               minsaturation=(Calibration_values["AvSat"]- Std_constant * Calibration_values["StdSat"]),
                               minvalue = min_value)
    Filtered = Filtered.invert()
    Filtered = Filtered.morphClose()
    #Filtered = Filtered.dilate(1) TO BE TESTED
    #Filtered = Filtered.erode(1)
    return Filtered


# Calibration procedure
def Calibration():
    blobs_threshold = 170
    flat_calibration_done = False
    while (not flat_calibration_done):  # Repeat until flat flap calibration is performed correctly
        flat_image = AcquireFlatImage()
        raw_input("Got the flat_image, now perform calibration")
        Calibration_coords = get_calibration_coordinates(flat_image)
        print "Approximate coordinates of flap: ", Calibration_coords
        Calibration_values = ColorAveraging(flat_image, Calibration_coords)
        filteredImage = apply_filter(Calibration_values, flat_image)
        possible_flaps = filteredImage.findBlobs(threshval = blobs_threshold)   #CAN ADD SIZES AND STUFF
        if possible_flaps > 1:
            possible_flaps.sortDistance(point =(Calibration_coords[0], Calibration_coords[1]))
        elif possible_flaps < 1:
            continue
        flap = possible_flaps[-1]
        flat_image.dl().rectangle2pts(flap.topLeftCorner(), flap.bottomRightCorner(),Color.RED, width = 5)
            #closest flap
        print "Is the flap marked with red square? Exit the image by left clicking and answer."
        disp = Display()  # Create a display
        while disp.isNotDone(): # Loop until display is not needed anymore
            if disp.mouseLeft:  #   Check if left click was used on display
                disp.done = True    # Turn off Display
            filteredImage.show()  # Show the image on Display
            time.sleep(1)           ##FOR DEBBUGING
            flat_image.show()
            time.sleep(1)
        Display().quit()    # Exit the display so it does not go to "Not responding"

        while True: # Loop until valid response
            userInput = raw_input("Was the flap in a red rectangle in the image? Please, enter Y or N.\n")
            userInput = userInput.lower()
            if userInput[0] == "y":
                flat_calibration_done = True
                break
            elif userInput[0] == "n":
                break
            else:
                print "Incorrect value entered."



## MAIN SOFTWARE

setup()
debug_mode = False  ##REPLACE WITH debug() for a question.
##Calibration supposed to be here.

## Main loop:
while True:
    Calibration()
