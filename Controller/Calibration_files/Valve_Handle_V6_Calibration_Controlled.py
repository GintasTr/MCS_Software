# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI

from SimpleCV import *
import cv2
from Controller import Valve_Handle_Controlled_V6

# prepares, selects the camera
def setup():
    global cam
    cam = Camera(0, {"width": 1024, "height": 768})        # Only for RPI 2592x1944. For calibration - 1024x768
    #cam = Camera()
    time.sleep(1)

# for image acquisition from camera (and flipping)
def GetImage():
    #img = cam.getImage()
    img = cam.getImage()                                    ##ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    img = img.flipVertical()
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


# Function to get the user confirmation about the image
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


# Function to ask inform the user of something
def inform_user(informationText):
    raw_input(informationText)


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


# Function for getting ValveCoords:
def GetValveCoords(img, RequestText):
    SQUARE_DIMENSIONS = 8
    print RequestText                                           # Ask user to click on display
    disp = Display(img.size())                                  # Create a display
    while disp.isNotDone():                                     # Loop until display is not needed anymore
        img.clearLayers()                                       # Clear old drawings
        if disp.mouseLeft:
            mouse_coords = [disp.mouseX, disp.mouseY]           # Show coords on screen with modifiable square size
            text = "X:" + str(mouse_coords[0]) + " Y:" + str(mouse_coords[1])
            img.dl().text(text, (mouse_coords[0] + 10, mouse_coords[1] + 10), color=Color.RED)
            img.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]], color = Color.RED,
                                       dimensions = [SQUARE_DIMENSIONS,SQUARE_DIMENSIONS])
        if disp.mouseRight:                                     # If right clicked
            disp.done = True                                    # Turn off Display
        img.save(disp)                                          # Show the image on Display
    Display().quit()                                            # Exit the display so it does not go to "Not responding"
    return mouse_coords                                         # Return mouseX and mouseY as mouse_coords[0] and [1]


# Function to ensure that correct blob was found
def correct_blob_confirmation(handle, img):
    TEXT_WHILE_IMAGE = "Look at the image and close it with mouse click or escape"
    QUESTION_TO_ASK = "Does the valve handle have red square around it in the picture? Y/N"

    test_img = img
    handle.drawMinRect(layer=test_img.dl(), color = Color.RED, width = 3)
    print TEXT_WHILE_IMAGE
    show_image_until_pressed(test_img)
    correct_blob = GetConfirmation(QUESTION_TO_ASK)
    return correct_blob


# Function to get the colour data of small area around certain point
def GetColourData(img, coords):
    CROP_SIZE = 8                                              # Area around the point to be evaluated (square width)

    cropped = img.crop(coords[0],                               # Adjust cropping area (x,y,w,h)
                       coords[1], CROP_SIZE,
                       CROP_SIZE, centered= True)
    cropped_num = cropped.getNumpyCv2()                             # Convert image to numpy array compatible with openCV
    cropped_num = cv2.cvtColor(cropped_num, cv2.COLOR_BGR2HSV)          # Convert image to HSV colour scheme with openCV
    meanHue = np.mean(cropped_num[:,:,0])                           # Slice the NumPy array to get the mean Hue
    meanSat = np.mean(cropped_num[:,:,1])                           # Slice the NumPy array to get the mean Sat
    stdSat = np.std(cropped_num[:,:,1])                             # Slice the NumPy array to get the std Sat
    minSat = np.min(cropped_num[:,:,1])                             # Slice the NumPy array to get the min Sat
    meanValue = np.mean(cropped_num[:,:,2])                         # Slice the NumPy array to get the mean Brightness
    # print meanHue, "- mean Hue"                                 # Print the obtained values for debugging
    # print meanSat, "- mean Sat"
    # print stdSat, "- std Sat"
    # print minSat, "- min Sat"
    # print meanValue, " - min Val"
    # raw_input("check results")                                  # FOR DEBUGGING

    hue_hist = cropped.hueHistogram()                               # Check if histogram rolls over (object is red.)
    if hue_hist[0] and hue_hist[1] and hue_hist[2] and hue_hist[-1] and hue_hist[-2] and hue_hist[-3] != 0:
        max_index = hue_hist.argmax()                               # If red, then get maximum hue histogram location
        print "Object is red, then average hue is: ", max_index     # Report issue
        meanHue = max_index                                         # Re-write Hue value

    hsv_data = {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    return hsv_data

# Function to write calibration results to file
def store_results(closed_coords_stored, closed_angle_stored, open_angle_stored,
                  closed_average_hue, closed_average_sat, closed_std_sat):
    FILE_NAME = "valve_handle_data.txt"
    storage = open(FILE_NAME, "w")
    storage.write("""valve_coord_x: %s
valve_coord_y: %s
closed_angle_stored: %s
open_angle_stored: %s
closed_average_hue: %s
closed_average_sat: %s
closed_std_sat: %s""" %(closed_coords_stored[0],closed_coords_stored[1], closed_angle_stored, open_angle_stored,
                  closed_average_hue, closed_average_sat, closed_std_sat))
    storage.close()
    print """valve_coord_x: %s
valve_coord_y: %s
closed_angle_stored: %s
open_angle_stored: %s
closed_average_hue: %s
closed_average_sat: %s
closed_std_sat: %s""" %(closed_coords_stored[0],closed_coords_stored[1], closed_angle_stored, open_angle_stored,
                  closed_average_hue, closed_average_sat, closed_std_sat)

# Function to get the required data (Type: Open or Closed)
def get_handle_data_Closed():
    USER_REQUEST = "Please put the camera as it would be during the ispection of the CLOSED valve handle."
    REQUEST_WHILE_IMAGE_SHOWN = "This is the image taken. Close the image by right clicking on it or pressing escape"
    CONFIRMATION_QUESTION = "Was the coolant valve handle clearly seen in the CLOSED position? Y/N"
    COORDINATES_REQUEST = "Pease left click on the valve handle to calibrate its " \
                          "coordinates and then right click to exit"


    closed_data_acquired = True
    while closed_data_acquired:
        # Get the closed valve handle image
        img_closed = RequestConfirmedImage(USER_REQUEST, REQUEST_WHILE_IMAGE_SHOWN,CONFIRMATION_QUESTION)

        # Get the coordinates of the valve
        closed_coords = GetValveCoords(img_closed,COORDINATES_REQUEST)

        # Get the average colour data around the selected part
        handle_colour_data = GetColourData(img_closed, closed_coords)
        #In format of: hsv_data = {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}

        # Try to detect the valve
        handle_found = Valve_Handle_Controlled_V6.HandleDetection(img_closed, closed_coords, handle_colour_data)
        # If valve was not found start again
        if handle_found == "No blobs found":
            print "Valve was not found, please continue the calibration again"
            continue

        # Check is valve was correctly found:
        if correct_blob_confirmation(handle_found, img_closed) == False:
            continue

        # Record closed handle angle
        closed_angle = handle_found.angle()

        # Return closed handle calibration data
        total_closed_data = {"colour_data": handle_colour_data,
                             "closed_coords": closed_coords,
                             "closed_angle": closed_angle}
        return total_closed_data

        # Exit the loop
        closed_data_acquired = False


# Function to get OPEN handle data:
def get_handle_data_Open(closed_coords, handle_colour_data):
    USER_REQUEST = "Please put the camera as it would be during the ispection of the OPEN valve handle."
    REQUEST_WHILE_IMAGE_SHOWN = "This is the image taken. Close the image by left clicking on it or pressing escape"
    CONFIRMATION_QUESTION = "Was the coolant valve handle clearly seen in the OPEN position? Y/N"

    open_data_acquired = True
    while open_data_acquired:
        # Get the open valve handle image
        img_open = RequestConfirmedImage(USER_REQUEST, REQUEST_WHILE_IMAGE_SHOWN, CONFIRMATION_QUESTION)

        # Try to detect the valve
        handle_found = Valve_Handle_Controlled_V6.HandleDetection(img_open, closed_coords, handle_colour_data)

        # If valve was not found start again
        if handle_found == "No blobs found":
            print "Valve was not found, please continue the calibration again. If this repeats, restart the software"
            continue

        # Check is valve was correctly found:
        if correct_blob_confirmation(handle_found, img_open) == False:
            continue

        # Record closed handle angle
        open_angle = handle_found.angle()

        # Return open handle calibration data
        return open_angle

        # Exit the loop
        closed_data_acquired = False


# Function to perform calibration
def perform_calibration():

    # Function to get the closed valve handle data (avg hue, avg sat, std sat, closed angle, click coords)
    closed_data = get_handle_data_Closed()
    # Function to get the open valve handle data (open anlge)
    open_angle = get_handle_data_Open(closed_data["closed_coords"], closed_data["colour_data"])
    #Results to store

    closed_coords_stored = closed_data["closed_coords"]
    closed_angle_stored = closed_data["closed_angle"]
    open_angle_stored = open_angle
    closed_average_hue = closed_data["colour_data"]["avg_hue"]
    closed_average_sat = closed_data["colour_data"]["avg_sat"]
    closed_std_sat = closed_data["colour_data"]["std_sat"]

    store_results(closed_coords_stored, closed_angle_stored, open_angle_stored,
                  closed_average_hue, closed_average_sat, closed_std_sat)


# MAIN SOFTWARE FUNCTION
def do_Calibration_procedure():
    # Initialisation:
    setup()                                                         # Perform camera setup
    perform_calibration()
    raw_input("Calibration Done. Saved as valve_handle_data.txt")



# If called by itself:
if __name__ == '__main__':
    print do_Calibration_procedure()