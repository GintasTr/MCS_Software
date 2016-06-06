from SimpleCV import *
from PalleteGeneration import Pallete_generation
from lepton_interface import Lepton_interface

class display_interaction():

    def __init__(self):
        self.pallete_object = Pallete_generation()
        self.pallete_numpy = self.pallete_object.get_pallete_numpy_array()

    # Colours the image according to pallete and values
    def colour_thermal_image(self, thermal_image_8bit):
        # Colour the image
        thermal_image_coloured = self.pallete_numpy[thermal_image_8bit]
        # Convert to RGB from BGR - takes ~0.01s
        thermal_image_coloured = cv2.cvtColor(thermal_image_coloured, cv2.COLOR_BGR2RGB)
        return thermal_image_coloured

    # Produces coloured, SCALLED image from raw data TODO: check performance other way around
    def coloured_image_from_raw(self,raw_values, image_scalar):
        STORED_IMAGE_NAME = "DetectionImage1.jpg"
        lepton_object = Lepton_interface()
        # Convert raw data to 8 bit image - takes 0.0008s
        bit8_image = lepton_object.raw_to_8bit(raw_values)
        bit8_image = bit8_image.astype(uint8)
        # Remove non-needed dimension
        bit8_image = bit8_image.squeeze()
        # Colour image takes ~0.005
        coloured_image = self.colour_thermal_image(bit8_image)
        # Scale 8 bit coloured image # CV_INTER_CUBIC might be used - slow but looks better. INTER_NEAREST.
        # INTER_LINEAR takes ~0.025s INTER_CUBIC - ~0.07s. Nearest - 0.01s
        coloured_image = cv2.resize(coloured_image, (0,0), None, image_scalar, image_scalar, cv2.INTER_LINEAR)
        # Takes ~0.2s, updated one takes ~0.0001s
        # cv2.imwrite(STORED_IMAGE_NAME, np.uint8(coloured_image)) # Write the image to file
        mat_array = cv.fromarray(coloured_image)
        # Take the image from file as SIMPLECV image. Updated one ~0.005s
        simplecv_img = Image(mat_array)
        # simplecv_img = Image(STORED_IMAGE_NAME)
        return simplecv_img


    # Combines acquired image, background image and legend layer
    def combine_image(self, coloured_scaled, legend_layer, background_image, hot_spots_layer):
        IMAGE_X_OFFSET = (background_image.height - coloured_scaled.height)/2
        # Add max temperature circles to coloured image - takes 0.00015s
        # Add coloured image to background image - takes 0.02s
        combined_image = background_image.blit(coloured_scaled, pos=(0,IMAGE_X_OFFSET))
        # Add legend layer and render it - takes 8*10^-5s
        combined_image.addDrawingLayer(legend_layer)
        combined_image.addDrawingLayer(hot_spots_layer)
        return combined_image


# 80x60 scaled to 960 x 720. So 80x60 * 10 = 800x720, widths are 80 and 80
# If called by itself:
if __name__ == '__main__':
    c = background_operations(800,80,80,720)
    img = c.get_background()
    legend_layer = c.get_legends_layer(50.1215,12.1516)
    disp = Display((960,720))
    img.addDrawingLayer(legend_layer)
    # img.applyLayers()
    while disp.isNotDone():
        img.show()

    raw_input()
