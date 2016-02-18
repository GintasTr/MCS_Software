from SimpleCV import *
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


def GetConfirmation(ConfirmationText):
    while True:                                                     # Loop until valid response
        print ConfirmationText                                      # Ask for confirmation
        try:                                                        # Catch Index error in case of too fast response
            userInput = raw_input()                                 # Check user input
            userInput = userInput.lower()                           # Make it lower case
            if userInput[0] == "y":                                 # Check if it is y, n, or something else
                return True                                         # Return respective values
            elif userInput[0] == "n":
                return False
        except(IndexError):                                         # In case of Index error (too fast response)
            print "Something is wrong, try again."
        else:
            print "Incorrect value entered."


# Function for getting the correct image
def RequestConfirmedImage(RequestText, ConfirmationText1, ConfirmationText2):
    confirmation = False                                        # Initialise the confimation loop
    while not confirmation:                                     # Loop until confirmation = True
        raw_input(RequestText)                                  # Show the request to put camera nicely.
        img = GetImage()                                        # Get image from camera
        print ConfirmationText1                                 # Ask to close the image and then answer
        disp = Display()                                        # Create a display
        while disp.isNotDone():                                 # Loop until display is not needed anymore
            if disp.mouseLeft:                                  # Check if left click was used on display
                disp.done = True                                # Turn off Display
            img.show()                                          # Show the image on Display
        Display().quit()                                        # Exit the display so it does not go to "Not responding"
        confirmation = GetConfirmation(ConfirmationText2)       # Ask whether LED was clearly visible and confirm.
    return img


# Function for getting mLedCoords:
def GetClickCoords(img, RequestText):
    print RequestText                                           # Ask user to click on display
    disp = Display()                                            # Create a display
    while disp.isNotDone():                                     # Loop until display is not needed anymore
        img.clearLayers()                                       # Clear old drawings
        if disp.mouseLeft:
            mouse_coords = [disp.mouseX, disp.mouseY]           # Show coords on screen with modifiable square size
            text = "X:" + str(mouse_coords[0]) + " Y:" + str(mouse_coords[1])
            img.dl().text(text, (mouse_coords[0] + 10, mouse_coords[1] + 10), color=Color.RED)
            img.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]], color = Color.RED, dimensions = [20,20])
        if disp.mouseRight:                                     # If right clicked
            disp.done = True                                    # Turn off Display
        img.save(disp)                                          # Show the image on Display
    Display().quit()                                            # Exit the display so it does not go to "Not responding"
    return mouse_coords                                         # Return mouseX and mouseY as mouse_coords[0] and [1]


# Function to detect the main LED:
def MainLedDetection(img, coords, data):
    Std_constant = 3                                            # Describes how many std dev of value to include
    min_value = 30                                              # Minimal illumination threshold
                                                                # Derive minimum saturation. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    minsaturation = (data["avg_sat"]- Std_constant * data["std_sat"])
    img = img.toHSV()                                           # Convert image to HSV colour space
    blobs_threshold = 220                                       # Specify blobs colour distance threshold
    blobs_min_size =  200                                       # Specify minimum blobs size
                                                                # Apply filters to the image TODO: calibrate or change the filtering
    filtered = img.hueDistance(color = data["avg_hue"],
                               minsaturation = minsaturation,
                               minvalue = min_value)
    filtered = filtered.invert()                                # Invert black and white (to have LED as white)
    filtered = filtered.morphClose()                            # Perform morphOps TODO: look for better options
    # filtered = filtered.dilate(1) #TO BE TESTED               # Possible morphOps options
    # Filtered = filtered.erode(1)
                                                                # Look for blobs
    all_blobs = filtered.findBlobs(threshval = blobs_threshold, minsize=blobs_min_size)
    if all_blobs > 1:                                           # If more than 1 blob found
        all_blobs.sortDistance(point =(coords[0], coords[1]))   # Sort based on distance from mouse click
        for i in range(0, len(all_blobs)):                      # For every found blob draw a rect on filtered image
                                                                # Only for debugging.
            filtered.dl().rectangle2pts(all_blobs[i].topLeftCorner(),
                                        all_blobs[i].bottomRightCorner(),Color.GREEN, width = 5)
            filtered.dl().text("%s" %i, (all_blobs[i].bottomRightCorner()), color=Color.RED)
    elif all_blobs < 1:                                         # If none blobs found
        print "No blobs found"                                  # Print and return that no blobs were found
        return "No blobs found"
    m_led = all_blobs[-1]                                       # m_led is the closes blob to the click
    return m_led


# Function to get the colour data of small area around certain point
def GetCalibrationData(img, coords):
    crop_size = 10                                              # Area around the point to be evaluated (square width)
    cropped = img.crop(coords[0],                               # Adjust cropping area (x,y,w,h)
                       coords[1], crop_size,
                       crop_size, centered= True)
    cropped.save("cropped.jpg")
    cropped = cropped.getNumpyCv2()                             # Convert image to numpy array compatible with openCV
    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)          # Convert image to HSV colour scheme with openCV
    meanHue = np.mean(cropped[:,:,0])                           # Slice the NumPy array to get the mean Hue
    meanSat = np.mean(cropped[:,:,1])                           # Slice the NumPy array to get the mean Sat
    stdSat = np.std(cropped[:,:,1])                             # Slice the NumPy array to get the std Sat
    minSat = np.min(cropped[:,:,1])                             # Slice the NumPy array to get the min Sat
    meanValue = np.mean(cropped[:,:,2])                         # Slice the NumPy array to get the mean Brightness
    # print meanHue, "- mean Hue"                                 # Print the obtained values for debugging
    # print meanSat, "- mean Sat"
    # print stdSat, "- std Sat"
    # print minSat, "- min Sat"
    # print meanValue, " - min Val"
    # raw_input("check results")                                  # FOR DEBUGGING

    hsv_data = {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    return hsv_data                                             # Return the obtained values


# Function to confirm whether main blob was found correctly
def ConfirmMainLed(img, blob, confirmationText, confirmationText2):
    print confirmationText
    disp = Display()                                            # Create a display
    while disp.isNotDone():                                     # Loop until display is not needed anymore
        img.dl().rectangle2pts(blob.topLeftCorner(), blob.bottomRightCorner(),Color.RED, width = 5)
        if disp.mouseLeft:                                      # Check if left click was used on display
            disp.done = True                                    # Turn off Display
        img.show()                                              # Show the image on Display
    Display().quit()    # Exit the display so it does not go to "Not responding"

    if not GetConfirmation(confirmationText2):
        return False
    return True


# Function to get the time of the sequence from user
def GetTime():
    while True:
        usr_input = raw_input("Please enter the time in integer seconds how long is one LED sequence going to be\n")
        try:
            usr_input = int(usr_input)
        except(ValueError):
            print"Please enter integer number"
            continue

        if ((type(usr_input) == int) and (usr_input > 0)):              # Check whether value is valid (int and >0)
            print "The sequence is going to last for %s seconds, is that correct? Y/N" % usr_input
            try:                                                        # Catch Index error in case of too fast response
                userInput = raw_input()                                 # Check user input
                userInput = userInput.lower()                           # Make it lower case
                if userInput[0] == "y":                                 # Check if it is y, n, or something else
                    return usr_input                                    # Return time stated
                elif userInput[0] == "n":
                    continue
            except(IndexError):                                     # In case of Index error (too fast response)
                    print "Something is wrong, try again."
        else:
            print "Incorrect value entered (please do not enter negative values)"


# Function to get the max distance between LEDs
def LedDistance(coords1, coords2):
    x_dist = abs(coords1[0] - coords2[0])                       # Get maximum X distance
    y_dist = abs(coords1[1] - coords2[1])                       # Get maximum Y distance
    max_dist = sqrt(x_dist**2 + y_dist**2)                      # Basic calculation of diagonal distance
    max_dist = int(round(max_dist))                             # Make max dist integer
    print x_dist                                                # For debugging
    print y_dist
    print max_dist
    return max_dist



# Main calibration function
def PerformCalibration():
    calibration_done = False                                    # Initialises loop
    while not calibration_done:                                 # Loop while calibration is not done
                                                                # Get and confirm the image from camera
        m_led_img = RequestConfirmedImage("Please put the camera as it would be during the LED sequence inspection. "
                                          "Press enter to take the image.",
                                          "Is the always lit up LED is clearly visible in the shown image? "
                                          "Press ESC or left click ON THE IMAGE to close the image and answer Y/N",
                                          "Was the always lit up LED clearly visible in the shown image? "
                                          "Please answer Y/N")
                                                                # Get the main LED coordinates
        m_led_coords = GetClickCoords(m_led_img, "In the shown image, left click on the always lit LED "
                                                 "to calibrate its location and brightness "
                                                 "and then Escape or Right click to turn off the image")
                                                                # Get main LED colour data = m_led_data
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
        m_led_data = GetCalibrationData(m_led_img, m_led_coords)
                                                                # Detect the Main LED blob
        m_led_blob = MainLedDetection(m_led_img, m_led_coords, m_led_data)
        if m_led_blob == "No blobs found":                      # If no leds were found
            continue                                            # Go to the start of the loop (take image again)
                                                                # Confirm that the blob was found correctly
        if not ConfirmMainLed(m_led_img, m_led_blob, "Can you see the red square around the LED? "
                                              "Press ESC or left click ON THE IMAGE to close it and answer Y/N",
                                              "Was the red square around the lit LED? Please answer Y/N"):
            continue                                            # If LED is not confirmed, start the loop again
        print "LED confirmed"                                   # For Debugging
                                                                # Get the second LED coordinates
        s_led_coords = GetClickCoords(m_led_img, "Please click on the LED which is "
                                                 "going to be blinking during the sequence and "
                                                 "then Right click or ESC to exit")
        print m_led_coords
        print s_led_coords                                      # For debugging
        seq_time = GetTime()                                    # Get the time of the sequence in seconds
        dist_led = LedDistance(m_led_coords, s_led_coords)      # Get the maximum distance between LEDs
                                                                # Warn the user about calibration
        print "Performing monitoring calibration. Please do not move for %s seconds" % seq_time



        while True:
            None


# Main software:
# Initialisation:

setup()
# TODO: Check for calibration data. If found, ask whether do calibration again. If not, go to calibration.

calibration_data=PerformCalibration()



while True:
    None
