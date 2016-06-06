from SimpleCV import *
import numpy as np
import cv2
from pylepton import Lepton


class Lepton_interface():

    def __init__(self):
        self.LEPTON_IMAGE_STORED = "Lepton_image.png"

    def get_raw_values(self):
        with Lepton() as l:                                     # Initialize lepton
            a,_ = l.capture()                                   # Capture the output
        return a

    # Function to filter only relevant output
    def filter_raw_range(self, raw_values): # TODO: find a way to filter out only relevant temperature
        pass

    # Process raw data to get 8 bit depth image
    def raw_to_8bit(self, raw_values):
        ###################### FIXED NORMALISATION WOULD GO HERE ####################################
        # raw_values = filter_raw_range(raw_values)
        cv2.normalize(raw_values, raw_values, 0, 65535, cv2.NORM_MINMAX)      # Normalize image
        bit8_image = np.right_shift(raw_values,8,raw_values)                      # Shift to 8 bit array
        return bit8_image

    # Function to get the image from the thermal camera
    def bit8_to_image(self, bit8_image):
        cv2.imwrite(self.LEPTON_IMAGE_STORED, np.uint8(bit8_image))           # Write the image to file
        simplecv_img = Image(self.LEPTON_IMAGE_STORED)                 # Take the image from file as SIMPLECV image
        return simplecv_img

    # To take new raw values and make it image
    def get_lepton_image_directly(self):
        raw_values = self.get_raw_values()
        bit8_image = self.raw_to_8bit(raw_values)
        img = self.bit8_to_image(bit8_image)
        return img