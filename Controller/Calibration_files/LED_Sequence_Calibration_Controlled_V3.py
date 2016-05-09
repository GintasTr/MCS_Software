# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

from SimpleCV import *
import cv2
from Controller import LED_Sequence_Controlled_V6

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


# Shows the image until the button is pressed
def show_image_until_pressed(img):
    disp = Display()                                        # Create a display
    while disp.isNotDone():                                 # Loop until display is not needed anymore
        if disp.mouseLeft:                                  # Check if left click was used on display
            disp.done = True                                # Turn off Display
        img.show()                                          # Show the image on Display
    Display().quit()                                        # Exit the display so it does not go to "Not responding"


# Briefly flashes the image
def show_image_briefly(img):
    img.show()                                              # Show the image on Display


# Function for getting the correct image
def RequestConfirmedImage(RequestText, ConfirmationText1, ConfirmationText2):
    confirmation = False                                        # Initialise the confimation loop
    while not confirmation:                                     # Loop until confirmation = True
        raw_input(RequestText)                                  # Show the request to put camera nicely.
        img = GetImage()             # Get image from camera
        print ConfirmationText1                                 # Ask to close the image and then answer
        disp = Display()                                        # Create a display
        while disp.isNotDone():                                 # Loop until display is not needed anymore
            if disp.mouseLeft:                                  # Check if left click was used on display
                disp.done = True                                # Turn off Display
            img.show()                                          # Show the image on Display
        Display().quit()                                        # Exit the display so it does not go to "Not responding"
        confirmation = GetConfirmation(ConfirmationText2)       # Ask whether LED was clearly visible and confirm.
    return img


# Function to get user confirmation about the image
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


# Function for getting mLedCoords:
def GetClickCoords(img, RequestText):
    RECT_DIMENSIONS = 30
    print RequestText                                           # Ask user to click on display
    disp = Display()                                            # Create a display
    while disp.isNotDone():                                     # Loop until display is not needed anymore
        img.clearLayers()                                       # Clear old drawings
        if disp.mouseLeft:
            mouse_coords = [disp.mouseX, disp.mouseY]           # Show coords on screen with modifiable square size
            text = "X:" + str(mouse_coords[0]) + " Y:" + str(mouse_coords[1])
            img.dl().text(text, (mouse_coords[0] + 10, mouse_coords[1] + 10), color=Color.RED)
            img.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]],
                                       color = Color.RED, dimensions = [RECT_DIMENSIONS,RECT_DIMENSIONS])
        if disp.mouseRight:                                     # If right clicked
            disp.done = True                                    # Turn off Display
        img.save(disp)                                          # Show the image on Display
    Display().quit()                                            # Exit the display so it does not go to "Not responding"
    return mouse_coords                                         # Return mouseX and mouseY as mouse_coords[0] and [1]


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


# Function to get the colour data of small area around certain point
def GetColourData(img, coords):
    BLOB_BRIGHTNESS_LIMIT = 230
    #CROPPING_AROUND_BLOB_SCALAR = 3
    CROP_SIZE = 30                                              # Area around the point to be evaluated (square width)
    cropped = img.crop(coords[0],                               # Adjust cropping area (x,y,w,h)
                       coords[1], CROP_SIZE,
                       CROP_SIZE, centered= True)
    show_image_until_pressed(cropped)

    cropped_num = cropped.getNumpyCv2()                         # Convert image to numpy array compatible with openCV
    cropped_num = cv2.cvtColor(cropped_num, cv2.COLOR_BGR2HSV)  # Convert image to HSV colour scheme with openCV

    meanHue = np.mean(cropped_num[:,:,0])                           # Slice the NumPy array to get the mean Hue
    meanSat = np.mean(cropped_num[:,:,1])                           # Slice the NumPy array to get the mean Sat
    stdSat = np.std(cropped_num[:,:,1])                             # Slice the NumPy array to get the std Sat
    # minSat = np.min(cropped_num[:,:,1])                             # Slice the NumPy array to get the min Sat
    # meanValue = np.mean(cropped_num[:,:,2])                         # Slice the NumPy array to get the mean Brightness
    # print meanHue, "- mean Hue"                                 # Print the obtained values for debugging
    # print meanSat, "- mean Sat"
    # print stdSat, "- std Sat"
    # print minSat, "- min Sat"
    # print meanValue, " - min Val"

    hue_hist = cropped.hueHistogram()                               # Check if histogram rolls over (object is red.)
    if hue_hist[0] and hue_hist[1] and hue_hist[2] and hue_hist[-1] and hue_hist[-2] and hue_hist[-3] != 0:
        max_index = hue_hist.argmax()                               # If red, then get maximum hue histogram location
        print "Object is red, then average hue is: ", max_index     # Report issue
        meanHue = max_index                                         # Re-write Hue value

    hsv_data = {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    return hsv_data                                             # Return the obtained values


# Function to get the time of the sequence from user
def GetTime():
    while True:
        usr_input = raw_input("Please enter the time in integer seconds how long is one LED sequence going to be:\n")
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
    return max_dist


# Main calibration function
def perform_calibration():
    calibration_done = False                                    # Initialises loop
    while not calibration_done:                                 # Loop while calibration is not done
                                                                # Get and confirm the image from camera
        m_led_img = RequestConfirmedImage(
                                          "Please put the camera as it would be during the LED sequence inspection. "
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
        m_led_data = GetColourData(m_led_img, m_led_coords)
                                                                # Detect the Main LED blob
        m_led_blob = LED_Sequence_Controlled_V6.MainLedDetection(m_led_img, m_led_coords, m_led_data)
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
        print m_led_coords, "are main LED coordinates"
        print s_led_coords, "are second LED coordinates"        # For debugging
        seq_time = GetTime()                                    # Get the time of the sequence in seconds
        dist_led = LedDistance(m_led_coords, s_led_coords)      # Get the maximum distance between LEDs
        scan_type = "unknown"                                   # Initialize scanning type variable
        if (3*dist_led*3*dist_led)/5 > m_led_blob.area():       # Check if main LED is more than 1/5th of total rectangle
                                                                # TODO modify 1/10
            scan_type = "number_of_blobs"                       # Scan based on number_of_blobs
        else:
            scan_type = "illumination_level"                    # Scan based on illumination_level

        print "Scan type is: ", scan_type                       # DEBUG - shows which scan type is active
        if scan_type == "illumination_level":                   # If scan is based on illumination_level
                                                                # Warn the user about calibration
            raw_input("Monitoring calibration is going to be performed. "
                      "Please do not move for %s seconds and ensure that flashing LED is flashing \n"
                      "Press enter to start" % seq_time)
                                                                    # Start sequence monitoring loop
            start = time.clock()                                    # Start timer
            elapsed_time_old = 0                                    # Initialise timer to measure elapsed time
            elapsed_time = time.clock() - start                     # Obtain value for while loop to not show error
            min_light = 255                                         # Initialise min light detection
            max_light = 0                                           # Initialise max light detection
            sequence_failed = False                                 # If not failed, then it is successful
            while(elapsed_time<seq_time):                           # Loop while sequence is not finished
                live_img = GetImage()                               # Obtain live image
                                                                    # Measure the illumination around LEDs
                area_light = LED_Sequence_Controlled_V6.GetLight(live_img, m_led_coords, m_led_data, dist_led)
                if area_light == "No blobs found":                  # Check whether No blobs were found
                    print "Lost main LED, please re-calibrate"      # Inform the user about "No blobs"
                    sequence_failed = True                          # When "break" out of loop, signal to start over
                    break                                           # Terminate the sequence and start calibration from top
                                                                    # TODO: Check if necessary to terminate, might continue
                if area_light > max_light:                          # Update max light
                    max_light = area_light
                if area_light < min_light:                          # Update min light
                    min_light = area_light
                elapsed_time = (time.clock() - start)               # Update the timer
            if sequence_failed:                                     # If sequence calibration failed, start over
                continue                                            # Return to top
                                                                    # Print the result for debugging
            print min_light, " is minimum light", max_light, "is maximum light"
            if max_light - min_light < 20:
                scan_type = "number_of_blobs"
                                                                    # Notify user about calibration
            print "CALIBRATION DONE. Values to be stored: ", "max light:", max_light, "min light:", min_light,\
                "main led coordintaes:", m_led_coords, "main led data:", m_led_data, "distance between leds:", dist_led,\
                "period of the sequence:", seq_time, "scan type:", scan_type
                                                                    # Store all obtained values TODO:save somewhere in file
            values = {"max_light": max_light, "min_light": min_light,"m_led_coords": m_led_coords,
                      "m_led_data": m_led_data, "dist_led": dist_led,"seq_time": seq_time, "scan_type": scan_type}
            calibration_done = True                                 # Stop the looping
            return values
        else:                                                       # If scan is based on number_of_blobs
            print "CALIBRATION DONE. Values to be stored: ","main led coordintaes:", m_led_coords, \
                "main led data:", m_led_data, "distance between leds:", dist_led,\
                "period of the sequence:", seq_time, "scan_type: ", scan_type
            values = {"m_led_coords": m_led_coords, "m_led_data": m_led_data, "dist_led": dist_led,"seq_time": seq_time,
                  "scan_type": scan_type}
            values["max_light"] = 0
            values["min_light"] = 0                                 # Fill in not-needed variables
            calibration_done = True                                 # Stop the looping
            return values


# Function to write calibration results to file, reminder: hsv_data = {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
def store_results(FILE_NAME, cal_data):
    with open(FILE_NAME, "w") as storage:
        storage.write("""m_led_coord_x: %s
m_led_coord_y: %s
avg_hue: %s
avg_sat: %s
std_sat: %s
dist_led: %s
seq_time: %s
scan_type: %s
max_light: %s
min_light: %s"""
                  % (cal_data["m_led_coords"][0],
                    cal_data["m_led_coords"][1],
                    cal_data["m_led_data"]["avg_hue"],
                    cal_data["m_led_data"]["avg_sat"],
                    cal_data["m_led_data"]["std_sat"],
                    cal_data["dist_led"],
                    cal_data["seq_time"],
                    cal_data["scan_type"],
                    cal_data["max_light"],
                    cal_data["min_light"]))
    print ("""m_led_coord_x: %s
m_led_coord_y: %s
avg_hue: %s
avg_sat: %s
std_sat: %s
dist_led: %s
seq_time: %s
scan_type: %s
max_light: %s
min_light: %s"""
                  % (cal_data["m_led_coords"][0],
                    cal_data["m_led_coords"][1],
                    cal_data["m_led_data"]["avg_hue"],
                    cal_data["m_led_data"]["avg_sat"],
                    cal_data["m_led_data"]["std_sat"],
                    cal_data["dist_led"],
                    cal_data["seq_time"],
                    cal_data["scan_type"],
                    cal_data["max_light"],
                    cal_data["min_light"]))


# MAIN SOFTWARE:
def do_calibration_procedure():
    STORAGE_FILE = "LED_sequence_calibration_data.txt"
    setup()                                                            # Perform camera setup

    calibration_data = perform_calibration()                           # Perform calibration procedure

    store_results(STORAGE_FILE, calibration_data)



# If called by itself, perform calibration
if __name__ == '__main__':
    do_calibration_procedure()