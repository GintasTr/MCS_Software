# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI
from SimpleCV import *
from Demonstration.Orange_flap_position_detection import Orange_Flap_Calibration_V3_Demo
from Demonstration.Orange_flap_position_detection import Orange_Flap_V5_Demo
from Demonstration.LED_Sequence_decoding import LED_Sequence_Calibration_Controlled_V4_Demo
from Demonstration.LED_Sequence_decoding import LED_Sequence_Controlled_V8_Demo
from Demonstration.Coolant_valve_handle_detection import Valve_Handle_Controlled_V7_Demo
from Demonstration.Coolant_valve_handle_detection import Valve_Handle_V6_Calibration_Demo
from Demonstration.Foreign_object_detection import Foreign_Object_Calibration_Controlled_V2_Demo
from Demonstration.Foreign_object_detection import Foreign_Object_Detection_Controlled_V3_Demo

def setup():
    global cam
    cam = Camera(0, {"width": 960, "height": 720})    # Only for RPI 2592x1944. For calibration - 1024x768
    #cam = Camera                                          # Only for laptop
    time.sleep(1)




# If called by itself:
if __name__ == '__main__':
    location_bit = 5
    setup()
    test_image = cam.getImage()
    display_test = Display((960,720))
    while display_test.isNotDone():
            test_image.show()

    time.sleep(5)
    Orange_Flap_V5_Demo.do_Orange_Flap_scanning(cam, location_bit)
    LED_Sequence_Controlled_V8_Demo.do_LED_scanning(cam, location_bit)
    Valve_Handle_Controlled_V7_Demo.do_Valve_Handle_scanning(cam)
    Foreign_Object_Detection_Controlled_V3_Demo.detect_foreign_object(cam, "red_object")




