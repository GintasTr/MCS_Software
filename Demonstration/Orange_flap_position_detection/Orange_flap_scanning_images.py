from SimpleCV import *

from Demonstration.show_images import Show_images


class orange_scanning_images():

    def __init__(self):
        self.IMAGE640 = Image("640Background.jpg")
        self.IMAGE1024 = Image("BlackBackground.gif")
        self.IMAGE960 = Image("960x720.jpg")

        self.BACKGROUND_IMAGE = self.IMAGE960

        self.screen = Show_images()
        #self.disp = Display((960, 720))  #((1024, 768))                              # Create a display


    def scanning_start(self):
        img = self.BACKGROUND_IMAGE

        img.dl().setFontSize(70)
        img.dl().text(
            "Orange flap detection",
            (210,img.height/3),
            # (img.width, img.width),
            color=Color.WHITE)
        img.dl().text(
            "Press Enter",
            (340,img.height - 150),
            # (img.width, img.width),
            color=Color.WHITE)

        self.screen.show_till_press_enter(img)


    def reading_from_file_image(self, coord_x, coord_y, flat_ratio, slope_ratio, colour_hue, colour_sat):
        img = self.BACKGROUND_IMAGE

        img.dl().setFontSize(70)
        img.dl().text(
            "Reading calibration data",
            (160,50),
            color=Color.WHITE)

        img.dl().setFontSize(45)
        # img.dl().text("%f" % round(angle_average,2))[0:2]
        # "%04i" % found_object_x
        text_temp = "Flap coordinates: X - %03i, Y - %03i" % (coord_x,coord_y)
        img.dl().text(
            text_temp,
            (120,250),
            color=Color.WHITE)
        text_temp = "W/H ratios: flat - %.2f, slope - %.2f" % (round(flat_ratio,3),round(slope_ratio,3))
        img.dl().text(
            text_temp,
            (120,300),
            color=Color.WHITE)
        text_temp = "Average colour data: Hue - %.1f, Sat - %.1f" % (round(colour_hue,2),round(colour_sat,2))
        img.dl().text(
            text_temp,
            (120,350),
            color=Color.WHITE)

        img.dl().setFontSize(70)
        img.dl().text(
            "Press Enter",
            (340,img.height - 100),
            # (img.width, img.width),
            color=Color.WHITE)

        self.screen.show_till_press_enter(img)


    def no_flaps_found(self, img):
        img.dl().setFontSize(70)
        img.dl().text(
            "Flap was not found",
            (245, 30),
            # (img.width, img.width),
            color=Color.WHITE)

        self.screen.show_image_briefly(img)

    def show_detected_orange_flap(self, img, detected_flap, FlapWHRatio, position, flat_ratio, slope_ratio):

        if position == "Flat":
            text_colour = Color.YELLOW
        else:
            text_colour = Color.RED


        img.dl().rectangle2pts(detected_flap.bottomLeftCorner(),
                               detected_flap.topRightCorner(),
                               text_colour, width = 3)

        img.dl().setFontSize(35)
        # to show the width:
        width_text = "%s" % detected_flap.width()
        width_x = int(detected_flap.bottomLeftCorner()[0] + detected_flap.width()/2 - 15)
        width_y = int(detected_flap.bottomLeftCorner()[1] + 5)
        img.dl().text(
            width_text,
            (width_x,width_y),
            color=text_colour)

        # to show the height:
        height_text = "%s" % detected_flap.height()
        height_x = int(detected_flap.bottomLeftCorner()[0] + detected_flap.width() + 5)
        height_y = int(detected_flap.bottomLeftCorner()[1] - detected_flap.height()/2 - 10)
        img.dl().text(
            height_text,
            (height_x,height_y),
            color=text_colour)


        img.dl().setFontSize(40)
        img.dl().text(
            ("Detected W/H ratio: %.3f" % (FlapWHRatio)),
            (20, 500),
            # (img.width, img.width),
            color=text_colour)
        img.dl().text(
            ("Flat W/H ratio: %.3f" % (flat_ratio)),
            (20, 540),
            # (img.width, img.width),
            color=Color.YELLOW)
        img.dl().text(
            ("Slope W/H ratio: %.3f" % (slope_ratio)),
            (20, 580),
            # (img.width, img.width),
            color=Color.RED)

        img.dl().setFontSize(60)
        img.dl().text(
            ("Flap position is: %s" % position),
            (200, 40),
            color = text_colour)

        self.screen.show_image_briefly(img)


if __name__ == '__main__':
    while True:
        img = Image("960x720.jpg")
        c = orange_calibration_images()
        c.scanning_start()
        # result = c.data_stored_image(354, 25, 2.54343, 1.4244, 243.24354, 144.5455)
        # print result
