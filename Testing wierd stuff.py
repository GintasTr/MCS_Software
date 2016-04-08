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
    min_brightness = 200                                        # Minimal illumination threshold
                                                                # Derive minimum saturation. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    minsaturation = (data["avg_sat"]- Std_constant * data["std_sat"])
    img = img.toHSV()                                           # Convert image to HSV colour space
    blobs_threshold = 200                                       # Specify blobs colour distance threshold
    blobs_min_size =  500                                       # Specify minimum blobs size
    blobs_max_size = 10000                                      # Specify max size of blob
                                                                # Apply filters to the image TODO: calibrate or change the filtering
    filtered = img.hueDistance(color = data["avg_hue"],
                               minsaturation = minsaturation,
                               minvalue = min_brightness)
    filtered = filtered.invert()                                # Invert black and white (to have LED as white)

    filtered = filtered.morphOpen()
                                                                # Look for blobs
    all_blobs = filtered.findBlobs(threshval = blobs_threshold, minsize=blobs_min_size, maxsize=blobs_max_size)
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
    show_image_until_pressed(filtered)
    # d= Display()                                               # For debugging
    # while d.isNotDone():
    #     filtered.show()
    # d.quit()
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




# Main calibration function
def PerformCalibration():
    calibration_done = False                                    # Initialises loop
    while not calibration_done:                                 # Loop while calibration is not done
                                                                # Get and confirm the image from camera
        m_led_img = Image("TESTINGIMAGE.jpg")
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
        if (2.5*dist_led*dist_led)/2 > m_led_blob.area():       # Check if main LED is more than 1/10th of total rectangle
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
                                                                    # Notify user about calibration
            print "CALIBRATION DONE. Values to be stored: ", "max light:", max_light, "min light:", min_light,\
                "main led coordintaes:", m_led_coords, "main led data:", m_led_data, "distance between leds:", dist_led,\
                "period of the sequence:", seq_time, "scan_type", scan_type
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
            return values



# Main software:
# Initialisation:

setup()                                                         # Perform camera setup
# TODO: Check for calibration data. If found, ask whether do calibration again. If not, go to calibration.

calibration_data=PerformCalibration()                           # Perform calibration procedure

raw_input("PRESS ENTER TO START MAIN SCANNING")
