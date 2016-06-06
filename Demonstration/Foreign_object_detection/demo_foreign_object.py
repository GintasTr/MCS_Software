# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI
from SimpleCV import *
from Demonstration.Foreign_object_detection import Foreign_Object_Calibration_Controlled_V2_Demo
from Demonstration.Foreign_object_detection import Foreign_Object_Detection_Controlled_V3_Demo


def setup():
    global cam
    cam = Camera(0, {"width": 960, "height": 720})    # Only for RPI 2592x1944. For calibration - 1024x768
    #cam = Camera                                          # Only for laptop
    time.sleep(1)




# If called by itself:
if __name__ == '__main__':
    setup()
    # object_name = Foreign_Object_Calibration_Controlled_V2_Demo.do_calibration_procedure(cam)
    Foreign_Object_Detection_Controlled_V3_Demo.detect_foreign_object(cam, "valve_handle")


    #
    # repeat_scanning = True
    # keep_asking = True
    # object_name = Foreign_Object_Calibration_Controlled_V2_Demo.do_calibration_procedure(cam)
    # while repeat_scanning:
    #     keep_asking = True
    #     Foreign_Object_Detection_Controlled_V3_Demo.detect_foreign_object(cam, object_name)
    #     while keep_asking:
    #         print "Scan again? Y/N"                                     # Ask for confirmation
    #         try:                                                        # Catch Index error in case of too fast response
    #             userInput = raw_input()                                 # Check user input
    #             userInput = userInput.lower()                           # Make it lower case
    #             if userInput[0] == "y":                                 # Check if it is y, n, or something else
    #                 keep_asking = False
    #                 continue
    #             elif userInput[0] == "n":
    #                 keep_asking = False
    #                 repeat_scanning = False
    #         except(IndexError):                                         # In case of Index error (too fast response)
    #             print "Something is wrong, try again."
    #         else:
    #             print "Incorrect value entered."
    # print "End of software."