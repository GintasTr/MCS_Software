from SimpleCV import *
from Demonstration.show_images import Show_images

class LED_scanning_images():

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
            "LED sequence detection",
            (205,img.height/3),
            # (img.width, img.width),
            color=Color.WHITE)
        img.dl().text(
            "Press Enter",
            (340,img.height - 150),
            # (img.width, img.width),
            color=Color.WHITE)

        self.screen.show_till_press_enter(img)


    def reading_from_file_image(self, m_led_coord_x, m_led_coord_y,
                                dist_led, seq_time, avg_hue, avg_sat):
        img = self.BACKGROUND_IMAGE

        img.dl().setFontSize(70)
        img.dl().text(
            "Reading calibration data",
            (160,50),
            color=Color.WHITE)

        img.dl().setFontSize(45)
        # img.dl().text("%f" % round(angle_average,2))[0:2]
        # "%04i" % found_object_x
        text_temp = "Main LED coordinates: X - %03i, Y - %03i" % (m_led_coord_x,m_led_coord_y)
        img.dl().text(
            text_temp,
            (120,250),
            color=Color.WHITE)
        text_temp = "Average colour data: Hue - %.1f, Sat - %.1f" % (round(avg_hue,2),round(avg_sat,2))
        img.dl().text(
            text_temp,
            (120,300),
            color=Color.WHITE)
        text_temp = "Distance between always on and flashing LED - %.2f" % (round(dist_led,2))
        img.dl().text(
            text_temp,
            (120,350),
            color=Color.WHITE)
        text_temp = "Sequence length - %i" % seq_time
        img.dl().text(
            text_temp,
            (120,400),
            color=Color.WHITE)


        img.dl().setFontSize(70)
        img.dl().text(
            "Press Enter",
            (340,img.height - 100),
            # (img.width, img.width),
            color=Color.WHITE)

        self.screen.show_till_press_enter(img)


    def looking_for_LED(self, img):
        img.dl().setFontSize(70)
        img.dl().text(
            "Looking for always on LED",
            (170, 30),
            # (img.width, img.width),
            color=Color.WHITE)

        return self.screen.show_briefly_till_n(img)

    def sequence_scanning_image_shown(self, img, main_blob,
                                      filtered_img_with_LEDs, crop_width,
                                      time_of_current_state, delta_T,
                                      number_of_blobs):

        img.dl().blit(filtered_img_with_LEDs, ((main_blob.coordinates()[0] - crop_width/2),
                                               main_blob.coordinates()[1] - crop_width/2))

        img.dl().centeredRectangle((main_blob.coordinates()[0],
                            main_blob.coordinates()[1]),(main_blob.width(),main_blob.height()),
                            color = Color.RED, width = 2)

        img.dl().rectangle2pts(
            ((main_blob.coordinates()[0] - crop_width/2), (main_blob.coordinates()[1] + crop_width/2)),
            ((main_blob.coordinates()[0] + crop_width/2), (main_blob.coordinates()[1] - crop_width/2)),
            color = Color.YELLOW, width = 2)


        if number_of_blobs > 1:
            state = "ON"
            previous_state = "OFF"
        else:
            state = "OFF"
            previous_state = "ON"

        img.dl().setFontSize(70)
        img.dl().text(
            ("LED is: %s for: %.1fs" % (state, round(time_of_current_state,1))),
            (240, 30),
            # (img.width, img.width),
            color=Color.WHITE)

        img.dl().setFontSize(50)
        img.dl().text(
            ("Previous state was %s and lasted for: %.2fs" % (previous_state, delta_T)),
            (120,img.height - 80),
            # (img.width, img.width),
            color=Color.WHITE)
        return self.screen.show_briefly_till_n(img)

    def non_valid_scan(self):
        img = self.BACKGROUND_IMAGE

        img.dl().setFontSize(70)
        img.dl().text(
            "Scanning results list:",
            (170,50),
            color=Color.WHITE)

        img.dl().setFontSize(45)

        img.dl().text(
            "Scanning results are not valid:",
            (120,250),
            color=Color.WHITE)
        img.dl().text(
            "Always on LED was not found for ",
            (120,300),
            color=Color.WHITE)
        img.dl().text(
            "more than half of the scan time",
            (120,350),
            color=Color.WHITE)

        img.dl().setFontSize(70)
        img.dl().text(
            "Press Enter",
            (340,img.height - 100),
            # (img.width, img.width),
            color=Color.WHITE)

        self.screen.show_till_press_enter(img)


    def scanning_done_image(self, results_list, average_period):
        img = self.BACKGROUND_IMAGE

        img.dl().setFontSize(70)
        img.dl().text(
            "Scanning results list:",
            (210, 50),
            color=Color.WHITE)

        img.dl().setFontSize(45)

        results_limit = 11
        iterator = range(1,results_limit)
        text_location = 120
        for i in iterator:
            img.dl().text(
            results_list[i],
            (100,text_location),
            color=Color.WHITE)
            text_location = text_location + 50

        img.dl().setFontSize(70)
        img.dl().text(
            ("Average period is: %s" % average_period),
            (210,img.height - 100),
            color=Color.WHITE)

        self.screen.show_till_press_enter(img)




if __name__ == '__main__':
    while True:
        img = Image("960x720.jpg")
        c = LED_scanning_images()
        c.non_valid_scan()
        # c.reading_from_file_image(354, 25, 2.54343, 5, 243.24354, 144.5455)
        # result = c.data_stored_image(354, 25, 2.54343, 1.4244, 243.24354, 144.5455)
        # print result
