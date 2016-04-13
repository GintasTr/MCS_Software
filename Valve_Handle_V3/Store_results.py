from SimpleCV import *
import cv2
from Setup import *
from User_Interface_Commands import *
from Calibration import *
from Camera_Wrapper import *
from Image_Processing import *
from Calibration import *

# Function to write calibration results to file
def store_results(closed_coords_stored, closed_angle_stored, open_angle_stored,
                  closed_average_hue, closed_average_sat, closed_std_sat):
    storage = open("storage.txt", "w")
    storage.write("""closed_coords_stored: %s
                     closed_angle_stored: %s
                     open_angle_stored: %s
                     closed_average_hue: %s
                     closed_average_sat: %s
                     closed_std_sat: %s
                     """ %(closed_coords_stored, closed_angle_stored, open_angle_stored,
                  closed_average_hue, closed_average_sat, closed_std_sat))
