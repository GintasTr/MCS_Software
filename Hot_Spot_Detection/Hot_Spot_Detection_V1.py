from SimpleCV import *
import numpy as np
import cv2
import math
from pylepton import Lepton


# Function to get raw values from thermal camera. Code from: https://github.com/groupgets/pylepton
def get_raw_values():
    with Lepton() as l:                                     # Initialize lepton
        a,_ = l.capture()                                   # Capture the output
    return a                                                # Return output


# Function to get the image from the thermal camera
def GetImage(raw_values):
    STORED_IMAGE_NAME = "CalibrationImage.jpg"
    #img = get_raw_values()                                  # Get raw image values
    cv2.normalize(raw_values, raw_values, 0, 65535, cv2.NORM_MINMAX)      # Normalize image
    np.right_shift(raw_values,8,raw_values)                               # Shift to 8 bit array
    cv2.imwrite(STORED_IMAGE_NAME, np.uint8(raw_values))           # Write the image to file
    simplecv_img = Image(STORED_IMAGE_NAME)                 # Take the image from file as SIMPLECV image
    return simplecv_img


# Function to get the confirmation from user
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



# Function to get the highest temperature data from single image
def get_max_temperature_data(raw_values):
    max_raw_pixel = raw_values.max()                        # Get the maximum pixel value
                                                            # Gets the maximum pixel value locations
    max_pixel_locations = np.where(raw_values == max_raw_pixel)
    max_pixel_locations_x_y =  zip(max_pixel_locations[0], max_pixel_locations[1])
                                                            # Return the dictionary of the data


    ### DEBUG:
    REPORT = "Max value is: " + str(max_raw_pixel) + " Max value location is: " + str(max_pixel_locations_x_y) + \
             " Its equivalent to: "+str(temperature_from_raw(max_raw_pixel))
    raw_input(REPORT)



    return {"max_raw_pixel": max_raw_pixel, "max_pixel_location": max_pixel_locations_x_y}


# Function to calculate temperature from raw value
def temperature_from_raw(max_raw_value):
    A = 0.1549                                              # Polynomial coefficients for T = 20C ambient
    B = 19.11
    C = 7454
                                                            # Polynomial fit inverse (-B + (B^2-4*A*C)^1/2)/(2*A)
    temperature = (-B + math.sqrt(B*B - 4*A*(C-max_raw_value)))/(2*A)

    return temperature


# Function to scan for highest temperature over several iterations
def iterate_for_max_temperature():
    ITERATIONS = 5                                                  # How many times to take image

    max_temperature_old = {"max_raw_pixel": 0, "max_pixel_location": 0, "max_temperature": 0}
                                                                    # Initialize variable

    for i in range(0, ITERATIONS-1):                                # Repeat as required by Iterations
        raw_values = get_raw_values()                               # Get camera output (raw values)
        max_temperature_new = get_max_temperature_data(raw_values)  # Get the maximum temperature from raw values
        max_temperature_new["max_temperature"] = temperature_from_raw(max_temperature_new["max_raw_pixel"])
                                                                    # Convert raw data to temperature
        if max_temperature_new["max_temperature"] > max_temperature_old["max_temperature"]:
            max_temperature_old = max_temperature_new               # If new temp is max, record new max temperature
        else:
            continue                                                # Else keep the old max temperature and continue
    return max_temperature_old                                      # Return the max temperature



# MAIN SOFTWARE:
# Initialisation:
# Nothing to initialise.

### Detection:
START_MESSAGE = "Starting hot spot detection"
TEMPERATURE_THRESHOLD = 50                                      # Threshold temperature for warning
WARNING_MESSAGE = "Warning, hot-spot (temperature larger than %i) detected: " \
                  "temperature of approximately %.1f at %i X and %i Y coordinates"
REGULAR_MESSAGE = "Hottest spot: temperature of approximately %.1f at %i X and %i Y coordinates"
AGAIN_TEXT = "Scanning is done. Scan again? Y/N"
FINISHED_PROMPT = "Sequence finished."

Warning = False                                                 # Initializing variables
scanning_done = False

while(not scanning_done):                                       # While not finished
    print START_MESSAGE                                         # Inform user about scanning

    max_temperature_information = iterate_for_max_temperature() # Collect maximum temperature pixel data
                                                                #  from multiple images

    if max_temperature_information["max_temperature"] > TEMPERATURE_THRESHOLD:
        Warning = True                                          # If max temp is larger than limit, flag the warning
        print WARNING_MESSAGE % (TEMPERATURE_THRESHOLD,         # Print message
                                 max_temperature_information["max_temperature"],
                                 max_temperature_information["max_pixel_location"][0],
                                 max_temperature_information["max_pixel_location"][1])
    else:                                                       # Else print regular message
        print REGULAR_MESSAGE % (max_temperature_information["max_temperature"],
                                 max_temperature_information["max_pixel_location"][0],
                                 max_temperature_information["max_pixel_location"][1])
    if GetConfirmation(AGAIN_TEXT):                             # Ask for another scan (REMOVE FOR REAL SOFTWARE)
        continue
    else:
        scanning_done = True                                    # Finish the loop

raw_input(FINISHED_PROMPT)                                      # Inform the user