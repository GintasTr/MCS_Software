from SimpleCV import *
from PalleteGeneration import Pallete_generation
from lepton_interface import Lepton_interface

class display_interaction():

    def __init__(self):
        self.pallete_object = Pallete_generation()

    # Shows the image until the button is pressed
    def show_image_until_pressed(self, img):
        disp = Display()                                        # Create a display
        while disp.isNotDone():                                 # Loop until display is not needed anymore
            if disp.mouseLeft:                                  # Check if left click was used on display
                disp.done = True                                # Turn off Display
            img.show()                                          # Show the image on Display
        Display().quit()                                        # Exit the display so it does not go to "Not responding"

    # Briefly flashes the image
    def show_image_briefly(self, img):
        img.show()                                              # Show the image on Display

    # Colours the image according to pallete and values
    def colour_thermal_image(self, thermal_image_8bit):
        # Get the pallete
        pallete = self.pallete_object.get_colormap()
        # NOT SURE IF NEEDED ###############################
        #thermal_image_8bit = cv2.cvtColor(thermal_image_8bit, cv2.COLOR_RGB2GRAY)
        thermal_image_coloured = thermal_image_8bit
        # Colour the image
        thermal_image_coloured = pallete[thermal_image_coloured]
        # Convert to RGB from BGR
        thermal_image_coloured = cv2.cvtColor(thermal_image_coloured, cv2.COLOR_BGR2RGB)
        return thermal_image_coloured

    # Produces coloured, SCALLED image from raw data TODO: check performance other way around
    def coloured_image_from_raw(self,raw_values, image_scalar):
        # Get Lepton interface object
        lepton_object = Lepton_interface()
        # Convert raw data to 8 bit image
        bit8_image = lepton_object.raw_to_8bit(raw_values)
        # Scale 8 bit image # CV_INTER_CUBIC might be used - slow but looks better
        bit8_image = cv2.resize(bit8_image, (0,0), None, image_scalar, image_scalar, cv2.INTER_LINEAR)
        # Colour scaled image
        coloured_image = self.colour_thermal_image(bit8_image)
        return coloured_image

    ###################################### ENDED HERE ####################################