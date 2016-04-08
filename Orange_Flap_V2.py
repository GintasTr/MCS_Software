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
        print "Was the flap clearly visible in the image? Please, enter Y or N."
        try:
            userInput = raw_input()
            userInput = userInput.lower()
            if userInput[0] == "y":
                return True
            elif userInput[0] == "n":
                return False
        except(IndexError):
            print "Pressed Enter before closing image"
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

def AcquireSlopeImage():  # Acquire flat flap image for calibration
    flat_image_done = False
    while (not flat_image_done):  # Repeat until flat flap image is acquired correctly
        raw_input(
            "Point camera the way it is going to be during the orange flap examination, "
            "flip the switch diagonaly (slope position) on the sub module and press Enter to take the image")
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
    meanHue = np.mean(cropped[:,:,0])
    meanSat = np.mean(cropped[:,:,1])
    stdSat = np.std(cropped[:,:,1])
    minSat = np.min(cropped[:,:,1])
    meanValue = np.mean(cropped[:,:,2])
    print meanHue, "- mean Hue"
    print meanSat, "- mean Sat"
    print stdSat, "- std Sat"
    print minSat, "- min Sat"
    #raw_input("check results")   --FOR DEBUGGING

    values = {"AvHue": meanHue, "AvSat": meanSat, "StdSat": stdSat}
    return values

def apply_filter(Calibration_values, img):
    Std_constant = 6 #TODO how much of illumination?
    min_value = 30 #minimal illumination of the object
    minsaturation = (Calibration_values["AvSat"]/2)
    img = img.toHSV()
    Filtered = img.hueDistance(color = Calibration_values["AvHue"],
                               minsaturation = minsaturation
                               #minvalue = min_value
                               )
    Filtered = Filtered.invert()
    #Filtered = Filtered.morphClose() #I THINK THIS SHOULD BE OPEN
    Filtered = Filtered.erode(1)
    Filtered = Filtered.dilate(2) #TODO test these morph ops...
    return Filtered


# Calibration procedure
def Flat_Calibration():     #TODO rearrange functions to avoid function-in function, to have only 1 variable passable in between
    blobs_threshold_flat = 130
    blobs_min_size_flat = 1000
    flat_calibration_done = False
    while (not flat_calibration_done):  # Repeat until flat flap calibration is performed correctly
        flat_image = AcquireFlatImage()
        raw_input("Got the flat_image, now perform calibration")
        Calibration_coords = get_calibration_coordinates(flat_image)
        print "Approximate coordinates of flap: ", Calibration_coords
        Calibration_values = ColorAveraging(flat_image, Calibration_coords)
        filteredImage = apply_filter(Calibration_values, flat_image)
        #TODO replace this here and everywhere else with function findAndSortBlobs.
        possible_flaps = filteredImage.findBlobs(threshval = blobs_threshold_flat, minsize=blobs_min_size_flat)   #CAN ADD SIZES AND STUFF
        if possible_flaps > 1:
            possible_flaps.sortDistance(point =(Calibration_coords[0], Calibration_coords[1]))
            for i in range(0, len(possible_flaps)):
                filteredImage.dl().rectangle2pts(possible_flaps[i].topLeftCorner(),
                                                 possible_flaps[i].bottomRightCorner(),Color.GREEN, width = 5)
                filteredImage.dl().text("%s" %i, (possible_flaps[i].topLeftCorner()), color=Color.RED)
                filteredImage.dl().circle(center = (Calibration_coords[0], Calibration_coords[1]), radius = 2,
                                          color = Color.RED, width = 3, filled = True)
        elif possible_flaps < 1:
            print "No possible flaps were found, starting calibration again"
            continue
        flap = possible_flaps[-1]
        flat_image.dl().rectangle2pts(flap.topLeftCorner(), flap.bottomRightCorner(),Color.RED, width = 5)
            #closest flap
        print "Is the flap marked with red square? Exit the image by left clicking and answer."
        disp = Display()  # Create a display
        while disp.isNotDone(): # Loop until display is not needed anymore
            if disp.mouseLeft:  #   Check if left click was used on display
                disp.done = True    # Turn off Display
            flat_image.show()  # Show the image on Display
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
    FlapWHRatio = flap.width() / flap.height()
    values = {"AvHue": Calibration_values["AvHue"], "AvSat": Calibration_values["AvSat"],
              "StdSat": Calibration_values["StdSat"], "FlatWHRatio": FlapWHRatio,
              "mouseX": Calibration_coords[0], "mouseY": Calibration_coords[1]}
    return values

def Slope_Calibration(AvHue,AvSat,StdSat,mouseX,mouseY):
    blobs_threshold_slope = 100
    blobs_min_size_slope = 1000
    slope_calibration_done = False
    while (not slope_calibration_done):
        slope_image = AcquireSlopeImage()
        filtered_image = apply_filter({"AvHue": AvHue, "AvSat": AvSat, "StdSat": StdSat}, slope_image)
        possible_flaps = filtered_image.findBlobs(threshval = blobs_threshold_slope, minsize=blobs_min_size_slope)   #CAN ADD SIZES AND STUFF
        if possible_flaps > 1:
            possible_flaps.sortDistance(point =(mouseX, mouseY))
            for i in range(0, len(possible_flaps)):
                filtered_image.dl().rectangle2pts(possible_flaps[i].topLeftCorner(),
                                                 possible_flaps[i].bottomRightCorner(),Color.GREEN, width = 5)
                filtered_image.dl().text("%s" %i, (possible_flaps[i].bottomRightCorner()), color=Color.RED)
        elif possible_flaps < 1:
            print "No flap was found, please take another picture"
            continue
        flap = possible_flaps[-1]
        slope_image.dl().rectangle2pts(flap.topLeftCorner(), flap.bottomRightCorner(),Color.RED, width = 5)

        print "Is the flap marked with red square? Exit the image by left clicking and answer."
        disp = Display()  # Create a display
        while disp.isNotDone(): # Loop until display is not needed anymore
            if disp.mouseLeft:  #   Check if left click was used on display
                disp.done = True    # Turn off Display
            slope_image.show()  # Show the image on Display
        Display().quit()    # Exit the display so it does not go to "Not responding"

        while True: # Loop until valid response
            userInput = raw_input("Was the flap in a red rectangle in the image? Please, enter Y or N.\n")
            userInput = userInput.lower()
            if userInput[0] == "y":
                slope_calibration_done = True
                break
            elif userInput[0] == "n":
                break
            else:
                print "Incorrect value entered."
    SlopeWHRatio = flap.width() / flap.height()
    return SlopeWHRatio



## MAIN SOFTWARE

setup()
debug_mode = False  ##REPLACE WITH debug() for a question.##TODO add debug_mode check where needed

#TODO calibrate these thresholds
blobs_threshold_main = 130   #thresholds for calibration blob detection and main process blob detection
blobs_min_size_main = 1000

flat_data = Flat_Calibration()
slope_data = Slope_Calibration(flat_data["AvHue"], flat_data["AvSat"], flat_data["StdSat"],
                                flat_data["mouseX"], flat_data["mouseY"])

## Main loop:
while True:
###TODO SOMETHING TO INITIATE, MAYBE STORE DATA SOMEWHERE ABOUT CALIBRATION
    time.sleep(1)   #So that not all the time it is checking, not usefull in real software
    Img = GetImage()
    Img = Img.toHSV()
    filtered = apply_filter(flat_data, Img)
    possible_flaps = filtered.findBlobs(threshval = blobs_threshold_main, minsize=blobs_min_size_main)
    if possible_flaps > 1:
        possible_flaps.sortDistance(point = (flat_data["mouseX"], flat_data["mouseY"]))
    elif possible_flaps < 1:
        print "No flaps found"
        continue
    possible_flaps.draw(width=3)
    filtered.show()
    flap = possible_flaps[-1]
    #Img.dl().rectangle2pts(flap.topLeftCorner(), flap.bottomRightCorner(),Color.RED, width = 5) #FOR FEEDBACK ONLY
    #Img.show()  #FOR FEEDBACK ONLY
    detectedRatio = flap.width()/flap.height()
    if detectedRatio > (flat_data["FlatWHRatio"]+2*slope_data) / 3:
        print "Flap is in slope position"
    elif detectedRatio <= (flat_data["FlatWHRatio"]+2*slope_data) / 3:
        print "Flap is in flat position"
    else:
        print "Detected incorrectly"