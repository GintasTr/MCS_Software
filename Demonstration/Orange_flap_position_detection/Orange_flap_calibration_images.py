from SimpleCV import *

from Demonstration.show_images import Show_images


class orange_calibration_images():

    def __init__(self):
        self.IMAGE640 = Image("640Background.jpg")
        self.IMAGE1024 = Image("BlackBackground.gif")
        self.IMAGE960 = Image("960x720.jpg")

        self.BACKGROUND_IMAGE = self.IMAGE960

        self.screen = Show_images()
        #self.disp = Display((960, 720))  #((1024, 768))                              # Create a display

    def calibration_start(self):
        img = self.BACKGROUND_IMAGE

        img.dl().setFontSize(70)
        img.dl().text(
            "Orange flap calibration",
            (200,img.height/3),
            # (img.width, img.width),
            color=Color.WHITE)
        img.dl().text(
            "Press Enter",
            (340,img.height - 150),
            # (img.width, img.width),
            color=Color.WHITE)

        self.screen.show_till_press_enter(img)


    def ask_for_flat_position(self):
        img = self.BACKGROUND_IMAGE

        img.dl().setFontSize(40)
        img.dl().text(
            "Place the camera as it would be during orange flap inspection",
            (60,img.height/3),
            # (img.width, img.width),
            color=Color.WHITE)
        img.dl().setFontSize(50)
        img.dl().text(
            "Put the orange flap to FLAT position",
            (180,img.height/3 + 50),
            # (img.width, img.width),
            color=Color.WHITE)
        img.dl().setFontSize(70)
        img.dl().text(
            "Press Enter",
            (340,img.height - 100),
            # (img.width, img.width),
            color=Color.WHITE)

        self.screen.show_till_press_enter(img)


    def ask_for_slope_position(self):
        img = self.BACKGROUND_IMAGE

        img.dl().setFontSize(40)
        img.dl().text(
            "Place the camera as it would be during orange flap inspection",
            (60,img.height/3),
            # (img.width, img.width),
            color=Color.WHITE)
        img.dl().setFontSize(50)
        img.dl().text(
            "Put the orange flap to SLOPE position",
            (180,img.height/3 + 50),
            # (img.width, img.width),
            color=Color.WHITE)
        img.dl().setFontSize(70)
        img.dl().text(
            "Press Enter",
            (340,img.height - 100),
            # (img.width, img.width),
            color=Color.WHITE)

        self.screen.show_till_press_enter(img)


    def ask_for_mouse_coords(self, img, crop_length):

        text_layer = DrawingLayer((img.width, img.height))

        text_layer.setFontSize(50)
        text_layer.text(
            "Left click on orange flap and press enter",
            (140, 30),
            # (img.width, img.width),
            color=Color.WHITE)
        text_layer.setFontSize(40)

        text_layer.text(
            "Press N if orange flap is not clearly seen in the image",
            (110,img.height - 80),
            # (img.width, img.width),
            color=Color.WHITE)

        local_result = self.screen.get_coords_YorN(img, crop_length, text_layer)
        return local_result


    def no_flaps_found(self, img):
        img.dl().setFontSize(70)
        img.dl().text(
            "Flap was not found",
            (245, 30),
            # (img.width, img.width),
            color=Color.WHITE)
        img.dl().text(
            "Press Enter",
            (340,img.height - 100),
            # (img.width, img.width),
            color=Color.WHITE)

        self.screen.show_till_press_enter(img)


    def show_detected_orange_flap(self, img, detected_flap, FlapWHRatio, position):

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


        img.dl().setFontSize(50)
        img.dl().text(
            "Press Y if orange flap was correctly found",
            (130, 30),
            # (img.width, img.width),
            color=Color.WHITE)
        img.dl().setFontSize(40)

        img.dl().text(
            "Press N if orange flap was not found correctly",
            (160,img.height - 80),
            # (img.width, img.width),
            color=Color.WHITE)


        img.dl().setFontSize(40)
        img.dl().text(
            ("%s W/H ratio: %.3f" % (position, FlapWHRatio)),
            (20, 540),
            # (img.width, img.width),
            color=text_colour)

        if self.screen.show_till_YorN(img):
            result_local = True
        else:
            result_local = False

        return result_local


    def data_stored_image(self, coord_x, coord_y, flat_ratio, slope_ratio, colour_hue, colour_sat):
        img = self.BACKGROUND_IMAGE

        img.dl().setFontSize(70)
        img.dl().text(
            "Data is recorded and stored",
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


if __name__ == '__main__':
    while True:
        img = Image("960x720.jpg")
        c = orange_calibration_images()
        result = c.data_stored_image(354, 25, 2.54343, 1.4244, 243.24354, 144.5455)
        print result
