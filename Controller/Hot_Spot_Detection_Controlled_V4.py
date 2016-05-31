# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".


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
    STORED_IMAGE_NAME = "DetectionImage1.jpg"
    #img = get_raw_values()                                  # Get raw image values
    cv2.normalize(raw_values, raw_values, 0, 65535, cv2.NORM_MINMAX)      # Normalize image
    np.right_shift(raw_values,8,raw_values)                               # Shift to 8 bit array
    cv2.imwrite(STORED_IMAGE_NAME, np.uint8(raw_values))           # Write the image to file
    simplecv_img = Image(STORED_IMAGE_NAME)                 # Take the image from file as SIMPLECV image
    return simplecv_img



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

    max_raw_pixel = raw_values.max()                                # Get the maximum pixel value
    max_pixel_locations = np.where(raw_values == max_raw_pixel)     # Gets the maximum pixel value locations
    max_pixel_locations_y = max_pixel_locations[0]                  # Assigns Y locations to hottest pixels
    max_pixel_locations_x = max_pixel_locations[1]                  # Assigns X locations to hottest pixels

    max_temperature = temperature_from_raw(max_raw_pixel)           # Gets the temperature equivalent of max raw value

    ### DEBUG:
    # REPORT = "Max value is: " + str(max_raw_pixel) + \
    #          " Max value locations are: X - " + str(max_pixel_locations_x) + \
    #          " Y - " + str(max_pixel_locations_y) + \
    #          ". Its equivalent to: " + str(max_temperature)
    # raw_input(REPORT)



    return {"max_raw_pixel": max_raw_pixel,                         # Return the dictionary of the data
            "max_pixel_locations_x": max_pixel_locations_x,
            "max_pixel_locations_y": max_pixel_locations_y,
            "max_temperature": max_temperature,
            "raw_values": raw_values}


# Function to calculate temperature from raw value
def temperature_from_raw(max_raw_value):
    A = 0.1205                                             # Polynomial coefficients for T = 20C ambient
    B = 21.791
    C = 7386
                                                            # Polynomial fit inverse (-B + (B^2-4*A*C)^1/2)/(2*A)
    temperature = (-B + math.sqrt(B*B - 4*A*(C-max_raw_value)))/(2*A)

    return temperature


# Function to scan for highest temperature over several iterations
def iterate_for_max_temperature():
    ITERATIONS = 5                                               # How many times to take image

    max_temperature_old = {"max_raw_pixel": 0,
                           "max_pixel_locations_x": 0,
                           "max_pixel_locations_y": 0,
                           "max_temperature": 0,
                           "raw_values": 0}
                                                                    # Initialize variable

    for i in range(0, ITERATIONS-1):                                # Repeat as required by Iterations
        time.sleep(0.2)
        raw_values = get_raw_values()                               # Get camera output (raw values)

        max_temperature_new = get_max_temperature_data(raw_values)  # Get the maximum temperature from raw values
        if max_temperature_new["max_temperature"] > max_temperature_old["max_temperature"]:
            max_temperature_old = max_temperature_new               # If new temp is max, record new max temperature
        else:
            continue                                                # Else keep the old max temperature and continue

    return max_temperature_old                                      # Return the max temperature

# MAIN SOFTWARE FUNCTION
def do_hot_spot_detection():
    # MAIN SOFTWARE:

    START_MESSAGE = "Starting hot spot detection"
    TEMPERATURE_THRESHOLD = 50                                      # Threshold temperature for warning
    WARNING_MESSAGE = "WARNING. HOT SPOT DETECTED!"
    REGULAR_MESSAGE = "Hottest spot: temperature of approximately %.1f at %i X and %i Y coordinates"

    Warning = False                                                 # Initializing variables

    print START_MESSAGE                                         # Inform user about scanning

# Collect maximum temperature pixel data from multiple images. Returns dictionary with:
# {"max_raw_pixel": max_raw_pixel,
# "max_pixel_locations_x": max_pixel_locations_x,
# "max_pixel_locations_y": max_pixel_locations_y,
# "max_temperature": max_temperature,
# "raw_values": raw_values}
    max_temperature_information = iterate_for_max_temperature()

    ## TO SHOW THE IMAGE
    RADIUS = 2
    IMAGE_SCALAR = 3
    image = GetImage(max_temperature_information["raw_values"])

    if max_temperature_information["max_temperature"] > TEMPERATURE_THRESHOLD:
        Warning = True                                          # If max temp is larger than limit, flag the warning
        print WARNING_MESSAGE                                   # Print message

                                                                # Print regular message either way
    for i in range (0, len(max_temperature_information["max_pixel_locations_x"])):
        print REGULAR_MESSAGE % (max_temperature_information["max_temperature"],
                                 max_temperature_information["max_pixel_locations_x"][i],
                                 max_temperature_information["max_pixel_locations_y"][i])


        ## TO SHOW THE IMAGE
        image.dl().circle((max_temperature_information["max_pixel_locations_x"][i],
                          max_temperature_information["max_pixel_locations_y"][i]),
                          RADIUS, color=Color.RED)


    ## TO SHOW THE IMAGE
    image = image.applyLayers()
    image = image.scale(IMAGE_SCALAR)
    show_image_until_pressed(image)

    fault_detection_feedback = ("%f" % round(max_temperature_information["max_temperature"],3))[0:5]
    hottest_spot_x = "%02i" % max_temperature_information["max_pixel_locations_x"][0]
    hottest_spot_y = "%02i" % max_temperature_information["max_pixel_locations_y"][0]
    fault_detection_output= {"fault_detection_feedback": fault_detection_feedback,
                           "max_pixel_locations_x": hottest_spot_x,
                           "max_pixel_locations_y": hottest_spot_y}
    # if Warning:
    #     return "Hot spot detected"
    # else:
    #     return "No hot spots detected"

    return fault_detection_output

# If called by itself:
if __name__ == '__main__':
    print do_hot_spot_detection()