# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI

from SimpleCV import *
import cv2
import LED_Sequence_Controlled_V8_Demo

# prepares, selects the camera
def setup(cam_local):
    global cam
    cam = cam_local

    # cam = Camera(0, {"width": 1024, "height": 768})        # Only for RPI 2592x1944. For calibration - 1024x768
    #cam = Camera()
    # time.sleep(1)


# for image acquisition from camera (and flipping)
def GetImage():
    img = cam.getImage()
    img = cam.getImage()                                    ##ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    #img = img.flipVertical()
    img = img.flipHorizontal()
    return img

# Shows the image until the button is pressed
def show_image_until_pressed(img):
    disp = Display()                                        # Create a display
    while disp.isNotDone():                                 # Loop until display is not needed anymore
        if disp.mouseLeft:                                  # Check if left click was used on display
            disp.done = True                                # Turn off Display
        img.show()                                          # Show the image on Display
    Display().quit()                                        # Exit the display so it does not go to "Not responding"

# Debugging function: Shows the pixel value when clicked on the screen:
def debug_pixel_value(img):
    disp = Display(img.size())                                            # Create a display
    while disp.isNotDone():                                     # Loop until display is not needed anymore
        img.clearLayers()                                       # Clear old drawings
        if disp.mouseLeft:
            mouse_coords = [disp.mouseX, disp.mouseY]           # Show coords on screen with modifiable square size
            text = str(img.getGrayPixel(mouse_coords[0],mouse_coords[1]))
            img.dl().text(text, (mouse_coords[0], mouse_coords[1]), color=Color.RED)
            img.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]], color = Color.RED, dimensions = [2,2])
        if disp.mouseRight:                                     # If right clicked
            disp.done = True                                    # Turn off Display
        img.save(disp)                                          # Show the image on Display
    Display().quit()                                            # Exit the display so it does not go to "Not responding"
    return mouse_coords



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
    RECT_DIMENSIONS = 5
    print RequestText                                           # Ask user to click on display
    disp = Display(img.size())                                  # Create a display
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
    #CROPPING_AROUND_BLOB_SCALAR = 3
    CROP_SIZE = 5                                             # Area around the point to be evaluated (square width)
    #  crop(self, x , y = None, w = None, h = None, centered=False)
    cropped = img.crop(coords[0],                               # Adjust cropping area (x,y,w,h)
                       coords[1], CROP_SIZE,
                       CROP_SIZE, centered= True)

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
    # # print minSat, "- min Sat"
    # # print meanValue, " - min Val"

    hue_hist = np.histogram(cropped.toHSV().getNumpy()[:,:,2], range = (0.0, 255.0), bins = 255)[0]  # Check if histogram rolls over (object is red.)


    if hue_hist[0] and hue_hist[-1]  != 0:
        max_index = hue_hist.argmax()                               # If red, then get maximum hue histogram location
        # print "Object is red, then average hue is: ", max_index     # Report issue
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
        m_led_blob = LED_Sequence_Controlled_V8_Demo.MainLedDetection(m_led_img, m_led_coords, m_led_data)
        if m_led_blob == "No blobs found":                      # If no leds were found
            print "No LEDs were found based on your calibration. Please, restart calibration"
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
        scan_type = "number_of_blobs"                                   # Initialize scanning type variable
        # if (3*dist_led*3*dist_led)/5 > m_led_blob.area():       # Check if main LED is more than 1/5th of total rectangle
        #                                                         # TODO modify 1/10
        #     scan_type = "number_of_blobs"                       # Scan based on number_of_blobs
        # else:
        #     scan_type = "illumination_level"                    # Scan based on illumination_level

        # print "Scan type is: ", scan_type                       # DEBUG - shows which scan type is active
        if scan_type == "number_of_blobs":                   # If scan is based on illumination_level
                                             # If scan is based on number_of_blobs
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
#     print ("""m_led_coord_x: %s                   DEBUGGING
# m_led_coord_y: %s
# avg_hue: %s
# avg_sat: %s
# std_sat: %s
# dist_led: %s
# seq_time: %s
# scan_type: %s
# max_light: %s
# min_light: %s"""
#                   % (cal_data["m_led_coords"][0],
#                     cal_data["m_led_coords"][1],
#                     cal_data["m_led_data"]["avg_hue"],
#                     cal_data["m_led_data"]["avg_sat"],
#                     cal_data["m_led_data"]["std_sat"],
#                     cal_data["dist_led"],
#                     cal_data["seq_time"],
#                     cal_data["scan_type"],
#                     cal_data["max_light"],
#                     cal_data["min_light"]))


# MAIN SOFTWARE:
def do_calibration_procedure(cam_local):
    STORAGE_FILE = "LED_sequence_calibration_data.txt"
    setup(cam_local)                                                            # Perform camera setup

    calibration_data = perform_calibration()                           # Perform calibration procedure

    store_results(STORAGE_FILE, calibration_data)



# If called by itself, perform calibration
if __name__ == '__main__':
    cam = Camera(0, {"width": 960, "height": 720})
    time.sleep(1)
    do_calibration_procedure(cam)