from SimpleCV import *
import numpy as np
import math
from lepton_interface import Lepton_interface

class Temperature_data:

    def __init__(self):
        self.poly_A = 0.1205                                             # Polynomial coefficients for temperature conversion
        self.poly_B = 21.791
        self.poly_C = 7386

    # Function to get the highest temperature data from single image
    def get_max_temperature_data(self, raw_values):

        max_raw_pixel = raw_values.max()                                # Get the maximum pixel value
        max_pixel_locations = np.where(raw_values == max_raw_pixel)     # Gets the maximum pixel value locations
        max_pixel_locations_y = max_pixel_locations[0]                  # Assigns Y locations to hottest pixels
        max_pixel_locations_x = max_pixel_locations[1]                  # Assigns X locations to hottest pixels

        max_temperature = self.temperature_from_raw(max_raw_pixel)           # Gets the temperature equivalent of max raw value

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
    def temperature_from_raw(self,max_raw_value):
        # Polynomial fit inverse (-B + (B^2-4*A*C)^1/2)/(2*A)
        temperature = (-self.poly_B + math.sqrt(self.poly_B*self.poly_B - 4*self.poly_A*(self.poly_C-max_raw_value)))/(2*self.poly_A)
        return temperature

    # Function to scan for highest temperature over several iterations
    def iterate_for_max_temperature(self):
        lepton_interface = Lepton_interface()
        ITERATIONS = 5                                               # How many times to take image
        max_temperature_old = {"max_raw_pixel": 0,
                               "max_pixel_locations_x": 0,
                               "max_pixel_locations_y": 0,
                               "max_temperature": 0,
                               "raw_values": 0}
                                                                        # Initialize variable
        for i in range(0, ITERATIONS-1):                                # Repeat as required by Iterations
            time.sleep(0.2)
            raw_values = lepton_interface.get_raw_values()              # Get camera output (raw values)
            max_temperature_new = self.get_max_temperature_data(raw_values)  # Get the maximum temperature from raw values
            if max_temperature_new["max_temperature"] > max_temperature_old["max_temperature"]:
                max_temperature_old = max_temperature_new               # If new temp is max, record new max temperature
            else:
                continue                                                # Else keep the old max temperature and continue

        return max_temperature_old                                      # Return the max temperature