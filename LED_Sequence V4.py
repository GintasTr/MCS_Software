from SimpleCV import *
import cv2


# prepares, selects the camera
def setup():
    global cam
    cam = Camera()
    time.sleep(1)

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
    min_brightness = 200                                        # Minimal illumination threshold
                                                                # Derive minimum saturation. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    img = img.toHSV()                                           # Convert image to HSV colour space
    blobs_max_size = 50000                                      # Specify max size of blob
                                                                # Apply filters to the image TODO: calibrate or change the filtering
    filtered = img.hueDistance(color = data["avg_hue"],
                               minvalue = min_brightness)
    filtered = filtered.invert()                                # Invert black and white (to have LED as white)
    filtered = filtered.morphOpen()                             # Perform morphOps
                                                                # Look for blobs
    all_blobs = filtered.findBlobs(maxsize=blobs_max_size)
    if all_blobs > 1:                                           # If more than 1 blob found
        all_blobs.sortDistance(point =(coords[0], coords[1]))   # Sort based on distance from mouse click
        for i in range(0, len(all_blobs)):                      # For every found blob draw a rect on filtered image
                                                                # Only for debugging. TODO: Remove these
            filtered.dl().rectangle2pts(all_blobs[i].topLeftCorner(),
                                        all_blobs[i].bottomRightCorner(),Color.GREEN, width = 5)
            filtered.dl().text("%s" %i, (all_blobs[i].bottomRightCorner()), color=Color.RED)
    elif all_blobs < 1:                                         # If none blobs found
        # print "No blobs found"                                # Print and return that no blobs were found. Not needed
        return "No blobs found"
    m_led = all_blobs[-1]                                       # m_led is the closest blob to mouse click
    return m_led


# Function to get the colour data of small area around certain point
def GetColourData(img, coords):
    crop_size = 20                                              # Area around the point to be evaluated (square width)
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
    print meanHue, "- mean Hue"                               # Print the obtained values for debugging
    # print meanSat, "- mean Sat"
    # print stdSat, "- std Sat"
    # print minSat, "- min Sat"
    print meanValue, " - min Val"
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

# Function to measure average illumination around LEDs TODO: Think about implementing threshold filter instead
def GetLight(img, coords, hsv_data, dist):
    dist_scalar = 3                                           # Margin of distance to include both LEDs
    crop_length = int(round(dist_scalar*dist))
    main_blob = MainLedDetection(img,coords,hsv_data)           # Get main led blob. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    if main_blob == "No blobs found":                           # Check whether blobs were found
        return "No blobs found"                                 # If no blobs found return string
    blob_coordinates = main_blob.coordinates()                  # Main blob coordinates
    cropped = img.crop(blob_coordinates[0],                     # Crop around the main blob
                        blob_coordinates[1], crop_length,
                        crop_length, centered=True)
    cropped = cropped.toGray()                                  # Convert to Gray scale colour space
    cropped.show()                                              # DEBUGGING
    cropped = cropped.getGrayNumpy()                            # Convert to NumPy array
    light_value = np.mean(cropped)                              # Get average grayscale colour
    # print light_value                                         # For debugging TODO: Check for more efficient methods
    return light_value



""" WORKING VERSION. DEBUGGING PROCESS.
# Function to measure average illumination around LEDs TODO: Think about implementing threshold filter instead
def GetLight(img, coords, hsv_data, dist):
    dist_scalar = 2.6                                           # Margin of distance to include both LEDs
    crop_length = int(round(dist_scalar*dist))
    main_blob = MainLedDetection(img,coords,hsv_data)           # Get main led blob. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    if main_blob == "No blobs found":                           # Check whether blobs were found
        return "No blobs found"                                 # If no blobs found return string
    blob_coordinates = main_blob.coordinates()                  # Main blob coordinates
    cropped = img.crop(blob_coordinates[0],                     # Crop around the main blob
                        blob_coordinates[1], crop_length,
                        crop_length, centered=True)
    cropped = cropped.toGray()                                  # Convert to Gray scale colour space
    cropped.show()                                              # DEBUGGING
    cropped = cropped.getGrayNumpy()                            # Convert to NumPy array
    light_value = np.mean(cropped)                              # Get average grayscale colour
    # print light_value                                         # For debugging TODO: Check for more efficient methods
    return light_value
"""


def BlobsNumber(img, coords, hsv_data, dist):
    dist_scalar = 3                                           # Margin of distance to include both LEDs
    crop_length = int(round(dist_scalar*dist))
    main_blob = MainLedDetection(img,coords,hsv_data)           # Get main led blob. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    if main_blob == "No blobs found":                           # Check whether blobs were found
        return "No blobs found"                                 # If no blobs found return string
    blob_coordinates = main_blob.coordinates()                  # Main blob coordinates
    cropped = img.crop(blob_coordinates[0],                     # Crop around the main blob
                        blob_coordinates[1], crop_length,
                        crop_length, centered=True)
    cropped = cropped.toGray()                                  # Convert to Grayscale Image
    cropped_num = cropped.getGrayNumpy()                        # Convert to NumPy array
    bin_thresh = (np.max(cropped_num)+np.mean(cropped_num))/2   # Set the threshold as half of the max to average
    cropped = cropped.binarize(thresh=bin_thresh)               # Binarize the cropped image
    cropped = cropped.invert()                                  # Invert so that light areas are white
    cropped = cropped.morphOpen()
    cropped = cropped.dilate(iterations=2)                      # If from close - change to 1
    cropped.show()
    all_blobs = cropped.findBlobs()
    if all_blobs<1:                           # Check whether blobs were found
        return "No blobs found"
                                                                # Find ALL blobs in the image
    all_blobs.draw(width=3)                                     # For debugging - draw all blobs
    cropped.show()
    #show_image_briefly(cropped)                                # DEBUGGING
    number_of_blobs = len(all_blobs)                            # Return the number of found blobs
    return number_of_blobs





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
        m_led_data = GetColourData(m_led_img, m_led_coords)
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
        print m_led_coords, "are main LED coordinates"
        print s_led_coords, "are second LED coordinates"        # For debugging
        seq_time = GetTime()                                    # Get the time of the sequence in seconds
        dist_led = LedDistance(m_led_coords, s_led_coords)      # Get the maximum distance between LEDs
        scan_type = "unknown"                                   # Initialize scanning type variable
        if (3*dist_led*3*dist_led)/5 > m_led_blob.area():       # Check if main LED is more than 1/5th of total rectangle
                                                                # TODO modify 1/10
            scan_type = "number of blobs"                       # Scan based on number of blobs
        else:
            scan_type = "illumination level"                    # Scan based on illumination level

        print "Scan type is: ", scan_type                       # DEBUG - shows which scan type is active
        if scan_type == "illumination level":                   # If scan is based on illumination level
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
                area_light = GetLight(live_img, m_led_coords, m_led_data, dist_led)
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
                scan_type = "number of blobs"
                                                                    # Notify user about calibration
            print "CALIBRATION DONE. Values to be stored: ", "max light:", max_light, "min light:", min_light,\
                "main led coordintaes:", m_led_coords, "main led data:", m_led_data, "distance between leds:", dist_led,\
                "period of the sequence:", seq_time, "scan type:", scan_type
                                                                    # Store all obtained values TODO:save somewhere in file
            values = {"max_light": max_light, "min_light": min_light,"m_led_coords": m_led_coords,
                      "m_led_data": m_led_data, "dist_led": dist_led,"seq_time": seq_time, "scan_type": scan_type}
            calibration_done = True                                 # Stop the looping
            return values
        else:                                                       # If scan is based on number of blobs
            print "CALIBRATION DONE. Values to be stored: ","main led coordintaes:", m_led_coords, \
                "main led data:", m_led_data, "distance between leds:", dist_led,\
                "period of the sequence:", seq_time, "scan_type: ", scan_type
            values = {"m_led_coords": m_led_coords, "m_led_data": m_led_data, "dist_led": dist_led,"seq_time": seq_time,
                  "scan_type": scan_type}
            calibration_done = True                                 # Stop the looping
            return values


# Function to perform the main sequence scanning
# Reminder: cal_data = {"max_light": max_light, "min_light": min_light,"m_led_coords": m_led_coords,
                      #"m_led_data": m_led_data, "dist_led": dist_led,"seq_time": seq_time, "scan_type": scan_type}
def SequenceScanning(cal_data):
    if cal_data["scan_type"] == "illumination level":            # Define the threshold between ON/OFF LED
        light_threshold = (cal_data["min_light"]+cal_data["max_light"])/2
    scan_done = False                                            # Initiate scanning loop
    while not scan_done:                                         # Perform while scanning is done
        led_sequence = []                                        # Create empty list to store sequence
        live_img = GetImage()                                    # Get live camera image
        if MainLedDetection(live_img ,cal_data["m_led_coords"],cal_data["m_led_data"]) == "No blobs found":
                                                                 # Check if there is a main LED
            continue                                             # Start from the top of the loop
        print "LED found, starting sequence scanning"            # Notify user about sequence scanning
        start = time.clock()                                     # Mark the start of sequence
        elapsed_old = 0                                          # Initialise for delta T acquisition
        previous_state = "Unknown"                               # Initialise previous LED state variable
        elapsed_time = time.clock() - start                      # Obtain value for while loop to not show error
        while(elapsed_time<cal_data["seq_time"]):                # Loop while sequence is not finished
            live_img = GetImage()                                # Obtain live image

            if cal_data["scan_type"] == "illumination level":        # If scanning is performed based on illumination
                light_level = GetLight(live_img, cal_data["m_led_coords"], cal_data["m_led_data"], cal_data["dist_led"])
                if light_level == "No blobs found":                  # If no blobs found
                    elapsed_time = (time.clock() - start)            # Get elapsed time for the list
                    led_sequence.append("No blobs found at %.4f" % round(elapsed_time,4))
                    print "No blobs found at %.4f" % round(elapsed_time,4)
                    continue
                if light_level > light_threshold:                    # Check if LED is ON of OFF
                    led_state = "ON"
                else:
                    led_state = "OFF"
                if previous_state == led_state:                      # If current state is the same as previous, do nothing
                    elapsed_time = (time.clock() - start)            # Update elapsed time for the loop
                    continue                                         # Loop again
                previous_state = led_state                           # Update the previous state
                elapsed_time = (time.clock() - start)                # Calculate elapsed time
                delta_t = elapsed_time - elapsed_old                 # Calculate Delta T
                elapsed_old = elapsed_time                           # Update Old time for delta T calculations
                                                                     # Add new values to sequence list
                led_sequence.append("LED state: %s at %.4f Delta T from last state: %.4f" %
                                    (led_state, round(elapsed_time,4), round(delta_t,4)))
                                                                     # Print new values for debugging
                print "LED state: %s at %.4f . Delta T from last state: %.4f" % (led_state, round(elapsed_time,4), round(delta_t,4))

            if cal_data["scan_type"] == "number of blobs":           # If scanning is performed based on number of blobs
                number_of_blobs = BlobsNumber(live_img, cal_data["m_led_coords"], cal_data["m_led_data"], cal_data["dist_led"])
                if number_of_blobs == "No blobs found":              # If no blobs were found
                    elapsed_time = (time.clock() - start)            # Get elapsed time for the list
                    led_sequence.append("No blobs found at %.4f" % round(elapsed_time,4))
                    print "No blobs found at %.4f" % round(elapsed_time,4)
                    continue                                         # Start from the top of the loop

                if number_of_blobs > 1:                              # Check if more than 1 LED is on
                    led_state = "ON"
                else:
                    led_state = "OFF"
                if previous_state == led_state:                      # If current state is the same as previous, do nothing
                    elapsed_time = (time.clock() - start)            # Update elapsed time for the loop
                    continue                                         # Loop again
                previous_state = led_state                           # Update the previous state
                elapsed_time = (time.clock() - start)                # Calculate elapsed time
                delta_t = elapsed_time - elapsed_old                 # Calculate Delta T
                elapsed_old = elapsed_time                           # Update Old time for delta T calculations
                                                                     # Add new values to sequence list
                led_sequence.append("LED state: %s at %.4f Delta T from last state: %.4f" %
                                    (led_state, round(elapsed_time,4), round(delta_t,4)))
                                                                     # Print new values for debugging
                print "LED state: %s at %.4f . Delta T from last state: %.4f" % (led_state, round(elapsed_time,4), round(delta_t,4))
                                                                 # Notify user about end of scanning
        print "END OF SCANNING. \n Sequence is:"                 # Nicely print the sequence
        for i in led_sequence:
            print i
        again = GetConfirmation("Scan again? Y/N")               # Ask if scan again
        if again:
            continue                                             # Start from the top loop
        return led_sequence                                      # TODO: Save it somewhere
                          # TODO: Save it somewhere


# Main software:
# Initialisation:

setup()                                                         # Perform camera setup
# TODO: Check for calibration data. If found, ask whether do calibration again. If not, go to calibration.

calibration_data=PerformCalibration()                           # Perform calibration procedure

raw_input("PRESS ENTER TO START MAIN SCANNING")
while True:
    led_sequence = SequenceScanning(calibration_data)                          # Start sequence scanning based on calibration data
    # Reminder: calibration_data = {"max_light": max_light, "min_light:": min_light,"m_led_coords": m_led_coords,
    # "m_led_data": m_led_data, "dist_led": dist_led,"seq_time": seq_time}
    raw_input("STOP")
