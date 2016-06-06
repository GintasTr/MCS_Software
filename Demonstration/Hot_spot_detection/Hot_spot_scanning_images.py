from SimpleCV import *

from Demonstration.show_images import Show_images


class hot_spot_scanning_images():

    def __init__(self):
        self.IMAGE960 = Image("960x720.jpg")
        self.BACKGROUND_IMAGE = self.IMAGE960
        self.screen = Show_images()
        #self.disp = Display((960, 720))  #((1024, 768))                              # Create a display


    def scanning_start(self):
        img = self.BACKGROUND_IMAGE

        img.dl().setFontSize(70)
        img.dl().text(
            "Hot spot detection",
            (250,img.height/3),
            # (img.width, img.width),
            color=Color.WHITE)
        img.dl().text(
            "Press Enter",
            (340,img.height - 150),
            # (img.width, img.width),
            color=Color.WHITE)

        self.screen.show_till_press_enter(img)

    def show_final_result(self, max_temperature, x_location, y_location):
        img.dl().setFontSize(70)
        img.dl().text(
            "Final result is:",
            (300, 50),
            color=Color.WHITE)
        img.dl().setFontSize(40)
        img.dl().text(
            ("Maximum detected temperature is: %s" %
             (max_temperature)),
            (125,300),
            # (img.width, img.width),
            color=Color.WHITE)

        img.dl().text(
            ("Detected temperature coordinates: X - %s, Y - %s" %
             (x_location,y_location)),
            (125,350),
            # (img.width, img.width),
            color=Color.WHITE)

        self.screen.show_till_press_enter(img)


if __name__ == '__main__':
    while True:
        img = Image("960x720.jpg")
        c = hot_spot_scanning_images()
        c.show_final_result("45.62", "12", "52")
        # result = c.data_stored_image(354, 25, 2.54343, 1.4244, 243.24354, 144.5455)
        # print result
