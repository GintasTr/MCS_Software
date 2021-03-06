# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI

from SimpleCV import *
import cv2

IMAGE640 = Image("640Background.jpg")
IMAGE1024 = Image("BlackBackground.gif")
IMAGE960 = Image("960x720.jpg")
BACKGROUND_IMAGE = IMAGE960

disp = Display((960, 720))  #((1024, 768))                              # Create a display


# Inform about the start
def calibration_start_image():
    img = BACKGROUND_IMAGE

    img.dl().setFontSize(70)
    img.dl().text(
        "Foreign object detection calibration",
        (85,img.height/3),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().text(
        "Press Enter",
        (370,img.height - 150),
        # (img.width, img.width),
        color=Color.WHITE)

    img.save(disp)

    while disp.isNotDone():                           # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_RETURN] == 1):                # Check if left click was used on display
            disp.done = True                          # Turn off Display
        img.show()                                    # Show the image on Display

    disp.done = False
    img.clearLayers()                                       # Clear old drawings


# Request for confirmed image
def request_of_confirmed_image():
    img = BACKGROUND_IMAGE

    img.dl().setFontSize(40)
    img.dl().text(
        "Place the camera as it would be during foreign object inspection",
        (70,img.height/3),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().setFontSize(50)
    img.dl().text(
        "Ensure that foreign object is visible by camera",
        (120,img.height/3 + 50),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().setFontSize(70)
    img.dl().text(
        "Press Enter",
        (370,img.height - 150),
        # (img.width, img.width),
        color=Color.WHITE)

    img.save(disp)

    while disp.isNotDone():                           # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_RETURN] == 1):                # Check if left click was used on display
            disp.done = True                          # Turn off Display
        img.show()                                    # Show the image on Display
    disp.done = False

    img.clearLayers()                                       # Clear old drawings
    #disp.quit()                                       # Exit the display so it does not go to "Not responding"


# Confirm that object is clearly seen
def object_clearly_seen(img):
    result = False
    img.dl().setFontSize(70)
    img.dl().text(
        "Is foreign object clearly visible?",
        (135, 40),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().text(
        "Press y/n",
        (400,img.height - 120),
        # (img.width, img.width),
        color=Color.WHITE)

    img.save(disp)

    while disp.isNotDone():                      # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_y] == 1):                # Check if y was pressed
            disp.done = True
            result = True
        elif(pressed[pg.K_n] == 1):              # Check if n was pressed
            disp.done = True
            result = False
        img.show()                                    # Show the image on Display
    disp.done = False

    img.clearLayers()                                       # Clear old drawings
    return result


# Get the coordinates of FO
def get_object_coords_image(img):
    CROP_DIMENSIONS = 8
    mouse_coords = None

    while disp.isNotDone():                                     # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()

        img.clearLayers()                                       # Clear old drawings

        img.dl().setFontSize(70)
        img.dl().text(
            "Left click on foreign object",
            (200, 40),
            # (img.width, img.width),
            color=Color.WHITE)
        img.dl().text(
            "Press Enter",
            (370,img.height - 120),
            # (img.width, img.width),
            color=Color.WHITE)


        if disp.mouseLeft:
            mouse_coords = [disp.mouseX, disp.mouseY]           # Show coords on screen with modifiable square size
            text = "X:" + str(mouse_coords[0]) + " Y:" + str(mouse_coords[1])
            img.dl().setFontSize(20)

            img.dl().text(text, (mouse_coords[0] + 10, mouse_coords[1] + 10), color=Color.RED)
            img.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]], color = Color.RED,
                                       dimensions = [CROP_DIMENSIONS,CROP_DIMENSIONS])
        if (pressed[pg.K_RETURN] == 1):                         # If enter pressed
            if mouse_coords != None:
                disp.done = True                                # Turn off Display
            else:
                print "Pressed Enter before clicking on image"
        img.save(disp)                                          # Show the image on Display
    disp.done = False
    img.clearLayers()                                       # Clear old drawings
    #Display().quit()                                            # Exit the display so it does not go to "Not responding"
    return mouse_coords                                         # Return mouseX and mouseY as mouse_coords[0] and [1]


# If object was not found
def object_not_found_image(img):
    img.dl().setFontSize(70)
    img.dl().text(
        "Object was not found",
        (255, 30),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().text(
        "Press Enter",
        (370,img.height - 120),
        # (img.width, img.width),
        color=Color.WHITE)

    img.save(disp)

    while disp.isNotDone():                      # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_RETURN] == 1):                # Check if y was pressed
            disp.done = True
        img.show()                                    # Show the image on Display
    disp.done = False
    img.clearLayers()                                       # Clear old drawings



# Confirm that object was correctly foun
def correct_object_confirmation_image(object_found, img):
    img.clearLayers()                                       # Clear old drawings
    result = False
    test_img = img

    object_found.drawMinRect(layer=test_img.dl(), color = Color.RED, width = 3, alpha=255)

    test_img.dl().setFontSize(45)
    test_img.dl().text(
        "Is foreign object with a red square around it?",
        (175, 40),
        # (img.width, img.width),
        color=Color.WHITE)
    test_img.dl().setFontSize(70)

    test_img.dl().text(
        "Press y/n",
        (400,test_img.height - 120),
        # (img.width, img.width),
        color=Color.WHITE)

    test_img.save(disp)

    while disp.isNotDone():                      # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_y] == 1):                # Check if y was pressed
            disp.done = True
            result = True
        elif(pressed[pg.K_n] == 1):              # Check if n was pressed
            disp.done = True
            result = False
        test_img.show()                          # Show the image on Display
    disp.done = False
    img.clearLayers()                                       # Clear old drawings
    return result


# Function to get name of the foreign object
def object_type_image():
    img = BACKGROUND_IMAGE

    img.dl().setFontSize(45)
    img.dl().text(
        "Close the image and enter name of the object to the terminal",
        (60, 300),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().text(
        "Press Enter",
        (390,img.height - 120),
        # (img.width, img.width),
        color=Color.WHITE)

    img.save(disp)

    while disp.isNotDone():                      # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_RETURN] == 1):                # Check if y was pressed
            disp.done = True
        img.show()                                    # Show the image on Display
    disp.done = False
    img.clearLayers()                                       # Clear old drawings


# Info about stored data
def store_calibration_data_image(object_coords_stored, object_name_stored, object_area_stored,
                  object_rect_distance_stored, object_aspect_ratio_stored,
                  object_average_hue, object_average_sat, object_std_sat):
    img = BACKGROUND_IMAGE

    img.dl().setFontSize(70)
    img.dl().text(
        "Data is recorded and stored",
        (180,50),
        color=Color.WHITE)

    img.dl().setFontSize(50)
    # img.dl().text("%f" % round(angle_average,2))[0:2]
    # "%04i" % found_object_x
    text_temp = "Object coordinates: X - %04i, Y - %04i" % (object_coords_stored[0],object_coords_stored[1])
    img.dl().text(
        text_temp,
        (150,200),
        color=Color.WHITE)
    text_temp = "Object name: %s" % object_name_stored
    img.dl().text(
        text_temp,
        (150,250),
        color=Color.WHITE)
    text_temp = "Object geometry: area - %i, aspect ratio - %.2f" % \
                (object_area_stored,round(object_aspect_ratio_stored,2))
    img.dl().text(
        text_temp,
        (150,300),
        color=Color.WHITE)
    text_temp = "Average colour data: Hue - %.1f, Sat - %.1f" % (round(object_average_hue,2),round(object_average_sat,2))
    img.dl().text(
        text_temp,
        (150,350),
        color=Color.WHITE)

    img.dl().setFontSize(70)
    img.dl().text(
        "Press Enter",
        (370,img.height - 150),
        # (img.width, img.width),
        color=Color.WHITE)

    img.save(disp)

    while disp.isNotDone():                           # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_RETURN] == 1):                # Check if left click was used on display
            disp.done = True                          # Turn off Display
        img.show()                                    # Show the image on Display
    disp.done = False
    img.clearLayers()                                       # Clear old drawings

    #disp.quit()                                       # Exit the display so it does not go to "Not responding"


if __name__ == '__main__':
    raw_input()
