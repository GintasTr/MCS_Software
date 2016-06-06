# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI
from SimpleCV import *
from Demonstration.LED_Sequence_decoding import LED_Sequence_Calibration_Controlled_V4_Demo
from Demonstration.LED_Sequence_decoding import LED_Sequence_Controlled_V8_Demo


def setup():
    global cam
    cam = Camera(0, {"width": 960, "height": 720})    # Only for RPI 2592x1944. For calibration - 1024x768
    #cam = Camera                                          # Only for laptop
    time.sleep(1)




# If called by itself:
if __name__ == '__main__':
    location_bit = 5
    setup()
    # LED_Sequence_Calibration_Controlled_V4_Demo.do_calibration_procedure(cam)
    LED_Sequence_Controlled_V8_Demo.do_LED_scanning(cam, location_bit)

