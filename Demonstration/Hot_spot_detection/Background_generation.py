from SimpleCV import *
from PalleteGeneration import Pallete_generation
from White_Background import White_background

class background_operations():

    def __init__(self):
        self.BACKGROUND_FILE_NAME = "Background.png"

    def combine_background(self, pallete_image, white_background_image):
        combined_image = white_background_image.blit(pallete_image,
                                                     pos = (white_background_image.width-pallete_image.width,0))
        return combined_image

    def get_background(self, shown_image_width, spacing_width, color_legend_width, shown_image_height):
        pallete_object = Pallete_generation()
        pallete_image = pallete_object.get_pallete_image(color_legend_width, shown_image_height)

        total_width = color_legend_width + spacing_width + shown_image_width
        white_background_object = White_background()
        white_background_image = white_background_object.get_white_background(total_width,shown_image_height)

        combined_background = self.combine_background(pallete_image,white_background_image)
        return combined_background

# If called by itself:
if __name__ == '__main__':
    c = background_operations()
    img = c.get_background(1000,50,30,700)
    disp = Display()
    while disp.isNotDone():
        img.show()

    raw_input()


