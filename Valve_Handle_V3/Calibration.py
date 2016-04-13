from SimpleCV import *
import cv2
from Setup import *
from User_Interface_Commands import *
from Camera_Wrapper import *
from Image_Processing import *



# Module responsible for calibration procedure

# Function to get the required data (Type: Open or Closed)
def get_handle_data_Closed():
    USER_REQUEST = "Please put the camera as it would be during the ispection of the CLOSED valve handle."
    REQUEST_WHILE_IMAGE_SHOWN = "This is the image taken. Close the image by right clicking on it or pressing escape"
    CONFIRMATION_QUESTION = "Was the coolant valve handle clearly seen in the CLOSED position? Y/N"
    COORDINATES_REQUEST = "Pease right click on the valve handle to calibrate its coordinates"


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
        handle_found = ValveDetection(img_closed, closed_coords, handle_colour_data)
        # If valve was not found start again
        if handle_found == "No blobs found":
            print "Valve was not found, please continue the calibration again"
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
    REQUEST_WHILE_IMAGE_SHOWN = "This is the image taken. Close the image by right clicking on it or pressing escape"
    CONFIRMATION_QUESTION = "Was the coolant valve handle clearly seen in the OPEN position? Y/N"

    open_data_acquired = True
    while open_data_acquired:
        # Get the open valve handle image
        img_open = RequestConfirmedImage(USER_REQUEST, REQUEST_WHILE_IMAGE_SHOWN, CONFIRMATION_QUESTION)

        # Try to detect the valve
        handle_found = ValveDetection(img_open, closed_coords, handle_colour_data)
        # If valve was not found start again
        if handle_found == "No blobs found":
            print "Valve was not found, please continue the calibration again"
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

