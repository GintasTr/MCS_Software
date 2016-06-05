from SimpleCV import *


class Show_images():

    def __init__(self):
        self.disp = Display((960, 720))  #((1024, 768))                              # Create a display


    def show_till_press_enter(self, img):
        img.save(self.disp)

        while self.disp.isNotDone():                           # Loop until display is not needed anymore
            pressed = pg.key.get_pressed()
            if(pressed[pg.K_RETURN] == 1):                # Check if left click was used on display
                self.disp.done = True                          # Turn off Display
            img.show()                                    # Show the image on Display

        img.clearLayers()                                       # Clear old drawings
        self.disp.done = False


    def show_till_YorN(self, img):
        img.save(self.disp)

        while self.disp.isNotDone():                      # Loop until display is not needed anymore
            pressed = pg.key.get_pressed()
            if(pressed[pg.K_y] == 1):                # Check if y was pressed
                self.disp.done = True
                result = True
            elif(pressed[pg.K_n] == 1):              # Check if n was pressed
                self.disp.done = True
                result = False
            img.show()                                    # Show the image on Display
        self.disp.done = False

        img.clearLayers()                                       # Clear old drawings
        return result


    def get_coords_YorN(self, img, crop_length, dl_with_text):
        local_result = None
        img.save(self.disp)

        while self.disp.isNotDone():                                # Loop until display is not needed anymore
            pressed = pg.key.get_pressed()

            dl_with_text.renderToOtherLayer(img.dl())

            if self.disp.mouseLeft:
                local_result = [self.disp.mouseX, self.disp.mouseY]           # Show coords on screen with modifiable square size
                text = "X:" + str(local_result[0]) + " Y:" + str(local_result[1])
                img.dl().setFontSize(20)
                img.dl().text(text, (local_result[0] + 10, local_result[1] + 10), color=Color.RED)
                img.dl().centeredRectangle(center = [local_result[0], local_result[1]], color = Color.RED,
                                           dimensions = [crop_length,crop_length])

            if (pressed[pg.K_RETURN] == 1):                         # If enter pressed

                if local_result is not None:
                    self.disp.done = True                                # Turn off Display
                else:
                    print "Pressed Enter before clicking on image"
            elif(pressed[pg.K_n] == 1):              # Check if n was pressed
                self.disp.done = True
                local_result = False

            img.save(self.disp)                # Show the image on Display
            img.clearLayers()

        self.disp.done = False
        img.clearLayers()                                       # Clear old drawings
        #Display().quit()                                            # Exit the display so it does not go to "Not responding"
        return local_result                                         # Return mouseX and mouseY as mouse_coords[0] and [1]


    def show_image_briefly(self, img):
        if self.disp.isNotDone:
            img.save(self.disp)                # Show the image on Display
            img.clearLayers()                  # Clear old drawings
        else:
            self.disp.isDone = False

    ####### DOES NOT WORK
    def show_briefly_till_n(self, img):
        img.save(self.disp)                # Show the image on Display
        pressed = pg.key.get_pressed()
        if (pressed[pg.K_n] == 1):                         # If n pressed
            img.clearLayers()                                       # Clear old drawings
            return False
        img.clearLayers()                                       # Clear old drawings
        return True