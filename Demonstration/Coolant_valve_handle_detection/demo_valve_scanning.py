# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

import sys                                                  # Only for RPI
import time
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI
from SimpleCV import *
from Demonstration.Coolant_valve_handle_detection import Valve_Handle_Controlled_V7_Demo
from Demonstration.Coolant_valve_handle_detection import Valve_Handle_V6_Calibration_Demo


def setup():
    global cam
    cam = Camera(0, {"width": 1024, "height": 768})    # Only for RPI 2592x1944. For calibration - 1024x768
    #cam = Camera                                          # Only for laptop
    time.sleep(1)




# If called by itself:
if __name__ == '__main__':
    setup()
    repeat_scanning = True
    keep_asking = True
    Valve_Handle_V6_Calibration_Demo.do_Calibration_procedure(cam)
    while repeat_scanning:
        keep_asking = True
        Valve_Handle_Controlled_V7_Demo.do_Valve_Handle_scanning(cam)
        while keep_asking:
            print "Scan again? Y/N"                                     # Ask for confirmation
            try:                                                        # Catch Index error in case of too fast response
                userInput = raw_input()                                 # Check user input
                userInput = userInput.lower()                           # Make it lower case
                if userInput[0] == "y":                                 # Check if it is y, n, or something else
                    keep_asking = False
                    continue
                elif userInput[0] == "n":
                    keep_asking = False
                    repeat_scanning = False
            except(IndexError):                                         # In case of Index error (too fast response)
                print "Something is wrong, try again."
            else:
                print "Incorrect value entered."
    print "End of software."