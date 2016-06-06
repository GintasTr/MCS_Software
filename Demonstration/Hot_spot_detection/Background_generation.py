from SimpleCV import *
from PalleteGeneration import Pallete_generation
from White_Background import White_background

class background_operations():

    def __init__(self, shown_image_width, spacing_width, color_legend_width, shown_image_height):
        self.BACKGROUND_FILE_NAME = "Background.png"
        self.shown_image_width = shown_image_width
        self.spacing_width = spacing_width
        self.color_legend_width = color_legend_width
        self.shown_image_height = shown_image_height

    # Combines white part and pallete
    def combine_background(self, pallete_image, white_background_image):
        combined_image = white_background_image.blit(pallete_image,
                                                     pos = (white_background_image.width-pallete_image.width,0))
        return combined_image

    # Returns the combined background
    def get_background(self):
        pallete_object = Pallete_generation()
        pallete_image = pallete_object.get_pallete_image(self.color_legend_width, self.shown_image_height)

        total_width = self.color_legend_width + self.spacing_width + self.shown_image_width
        white_background_object = White_background()
        white_background_image = white_background_object.get_black_background(total_width, self.shown_image_height)

        combined_background = self.combine_background(pallete_image,white_background_image)
        return combined_background

    # Add legend temperatures to the image
    def get_legends_layer(self, max_temperature, min_temperature):
        NUMBER_OF_ENTRIES = 6
        BOTTOM_NUMBER_OFFSET = 30
        LEGEND_X_OFFSET = 65
        FONT_SIZE = 45
        # Initialise lists and drawing layer
        combined_width = self.shown_image_width + self.spacing_width + self.color_legend_width
        legend_layer = DrawingLayer((combined_width,self.shown_image_height))
        text_values = range(NUMBER_OF_ENTRIES)
        text_locations = range(NUMBER_OF_ENTRIES)
        # Get the temperature and location between entries
        temperature_scalar = (max_temperature - min_temperature)/(NUMBER_OF_ENTRIES-1)
        location_scalar = self.shown_image_height/(NUMBER_OF_ENTRIES - 1)
        # Record values and locations, insert text to drawing layer
        for i in range(NUMBER_OF_ENTRIES):
            text_values[i] = "%.1f" % round((max_temperature - temperature_scalar*i), 1)
            text_locations[i] = int(round(location_scalar*i))
        text_locations[-1] = text_locations[-1] - BOTTOM_NUMBER_OFFSET
        # Insert text to drawing layer
        legend_layer.setFontSize(FONT_SIZE)
        for i in range(len(text_values)):
            legend_layer.text(text_values[i],
                              ((self.shown_image_width + self.spacing_width - LEGEND_X_OFFSET),
                               (text_locations[i])),
                              color = Color.WHITE)
        return legend_layer




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


